
using System;
using System.Collections.Generic;
using System.Collections.Concurrent;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Diagnostics;

public static class batch_upload_advanced {

    // Configuration - Replace with your actual values
    public static string API_KEY = "<your-api-key>";
    public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>";   // 你的知識庫 ID
    public static string FILES_DIRECTORY = "<your-files-directory>";    // 你要上傳的檔案目錄

    public class UploadConfig {
        public int max_concurrent_uploads { get; set; } = 10;
        public int max_retries { get; set; } = 3;
        public double retry_delay { get; set; } = 2.0;
        public int timeout_seconds { get; set; } = 300;
    }

    public enum UploadStatus {
        PENDING,
        UPLOADING,
        SUCCESS,
        FAILED,
        SKIPPED
    }

    public class FileUploadTask {
        public string file_path { get; set; }
        public long file_size { get; set; }
        public UploadStatus status { get; set; } = UploadStatus.PENDING;
        public string error_message { get; set; }
        public double? upload_time { get; set; }
        public int retry_count { get; set; } = 0;
        public string knowledge_file_id { get; set; }  // 記錄上傳後的 knowledge file ID
    }

    public class BatchFileUploaderAdvanced {
        private string api_key;
        private string knowledge_base_id;
        private UploadConfig config;
        private string base_url;
        private string source_directory;

        // 使用線程鎖來防止並發寫入 checkpoint 的問題
        private readonly object checkpoint_lock = new object();
        private readonly object completed_lock = new object();

        // 設定輸出資料夾結構
        private string output_dir;
        private string checkpoint_dir;
        private string log_dir;
        private string report_dir;
        private string checkpoint_file;

        private ConcurrentQueue<FileUploadTask> tasks_queue = new ConcurrentQueue<FileUploadTask>();
        private List<FileUploadTask> completed_tasks = new List<FileUploadTask>();
        private List<FileUploadTask> failed_tasks = new List<FileUploadTask>();

        private StreamWriter log_writer;
        private bool shutdown = false;

        public BatchFileUploaderAdvanced(
            string apiKey,
            string knowledgeBaseId,
            UploadConfig uploadConfig,
            string baseUrl = "https://api.maiagent.ai/api/v1/",
            string sourceDirectory = null
        ) {
            this.api_key = apiKey;
            this.knowledge_base_id = knowledgeBaseId;
            this.config = uploadConfig;
            this.base_url = baseUrl;
            this.source_directory = sourceDirectory;

            // 設定輸出資料夾結構 - 使用來源資料夾名稱和知識庫ID組合
            string folder_name;
            if (!string.IsNullOrEmpty(sourceDirectory)) {
                folder_name = Path.GetFileName(Path.GetFullPath(sourceDirectory).TrimEnd(Path.DirectorySeparatorChar));
            } else {
                folder_name = "default";
            }

            // 創建唯一的輸出目錄：資料夾名稱_知識庫ID
            string unique_dir_name = $"{folder_name}_{knowledgeBaseId.Substring(0, Math.Min(8, knowledgeBaseId.Length))}";
            // 輸出到與程式同一目錄下
            string program_dir = Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location);
            this.output_dir = Path.Combine(program_dir, "upload_outputs", unique_dir_name);
            this.checkpoint_dir = Path.Combine(output_dir, "checkpoints");
            this.log_dir = Path.Combine(output_dir, "logs");
            this.report_dir = Path.Combine(output_dir, "reports");

            // 建立所有必要的資料夾
            Directory.CreateDirectory(checkpoint_dir);
            Directory.CreateDirectory(log_dir);
            Directory.CreateDirectory(report_dir);

            // 使用固定的 checkpoint 檔名
            this.checkpoint_file = Path.Combine(checkpoint_dir, "upload_checkpoint.json");

            // 設定日誌
            var log_filename = Path.Combine(log_dir, $"upload_log_{DateTime.Now:yyyyMMdd_HHmmss}.log");
            log_writer = new StreamWriter(log_filename, true) { AutoFlush = true };

            // 設定中斷處理
            Console.CancelKeyPress += (sender, e) => {
                e.Cancel = true;
                LogInfo("Received interrupt signal. Saving checkpoint...");
                shutdown = true;
                save_checkpoint();
                Environment.Exit(0);
            };
        }

        private void LogInfo(string message) {
            var logMessage = $"{DateTime.Now:yyyy-MM-dd HH:mm:ss} - INFO - {message}";
            Console.WriteLine(logMessage);
            log_writer?.WriteLine(logMessage);
        }

        private void LogWarning(string message) {
            var logMessage = $"{DateTime.Now:yyyy-MM-dd HH:mm:ss} - WARNING - {message}";
            Console.WriteLine(logMessage);
            log_writer?.WriteLine(logMessage);
        }

        private void LogError(string message) {
            var logMessage = $"{DateTime.Now:yyyy-MM-dd HH:mm:ss} - ERROR - {message}";
            Console.WriteLine(logMessage);
            log_writer?.WriteLine(logMessage);
        }

        public List<FileUploadTask> scan_files(string directory) {
            // 掃描目錄並建立上傳任務列表
            var tasks = new List<FileUploadTask>();

            foreach (var file_path in Directory.EnumerateFiles(directory, "*", SearchOption.AllDirectories)) {
                var filename = Path.GetFileName(file_path);
                if (!filename.StartsWith(".")) {
                    try {
                        var file_info = new FileInfo(file_path);
                        tasks.Add(new FileUploadTask {
                            file_path = file_path,
                            file_size = file_info.Length
                        });
                    } catch (Exception e) {
                        LogWarning($"Cannot access file {file_path}: {e.Message}");
                    }
                }
            }

            return tasks;
        }

        public Dictionary<string, object> load_checkpoint() {
            // 載入檢查點以恢復中斷的上傳
            if (!File.Exists(checkpoint_file)) {
                return null;
            }

            try {
                var jsonString = File.ReadAllText(checkpoint_file);
                var checkpoint_data = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(jsonString);

                var completed_files = new List<string>();
                if (checkpoint_data.ContainsKey("completed_files")) {
                    completed_files = JsonSerializer.Deserialize<List<string>>(checkpoint_data["completed_files"].GetRawText());
                }

                LogInfo($"Loaded checkpoint with {completed_files.Count} completed files");

                // Convert JsonElement to object for easier access
                var result = new Dictionary<string, object>();
                foreach (var kvp in checkpoint_data) {
                    result[kvp.Key] = kvp.Value;
                }
                return result;

            } catch (Exception e) {
                LogError($"Failed to load checkpoint: {e.Message}");
                return null;
            }
        }

        public void save_checkpoint() {
            // 儲存當前進度 - 累積更新已完成檔案
            lock (checkpoint_lock) {
                // 載入現有的 checkpoint（如果存在）
                var existing_completed = new HashSet<string>();
                var existing_failed = new List<Tuple<string, string>>();
                var existing_file_id_mapping = new Dictionary<string, string>();

                if (File.Exists(checkpoint_file)) {
                    try {
                        var jsonString = File.ReadAllText(checkpoint_file);
                        var existing_data = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(jsonString);

                        if (existing_data.ContainsKey("completed_files")) {
                            var completed_list = JsonSerializer.Deserialize<List<string>>(existing_data["completed_files"].GetRawText());
                            existing_completed = new HashSet<string>(completed_list);
                        }

                        if (existing_data.ContainsKey("failed_files")) {
                            var failed_list = JsonSerializer.Deserialize<List<List<string>>>(existing_data["failed_files"].GetRawText());
                            foreach (var item in failed_list) {
                                if (item.Count >= 2) {
                                    existing_failed.Add(new Tuple<string, string>(item[0], item[1]));
                                }
                            }
                        }

                        if (existing_data.ContainsKey("file_id_mapping")) {
                            existing_file_id_mapping = JsonSerializer.Deserialize<Dictionary<string, string>>(
                                existing_data["file_id_mapping"].GetRawText()
                            );
                        }
                    } catch (Exception e) {
                        LogWarning($"Could not read existing checkpoint: {e.Message}");
                    }
                }

                // 合併新的已完成檔案
                lock (completed_lock) {
                    foreach (var task in completed_tasks) {
                        existing_completed.Add(task.file_path);
                    }
                }

                // 合併失敗檔案（去除重複）
                var failed_paths = new HashSet<string>(existing_failed.Select(t => t.Item1));
                foreach (var task in failed_tasks) {
                    if (!failed_paths.Contains(task.file_path)) {
                        existing_failed.Add(new Tuple<string, string>(task.file_path, task.error_message));
                        failed_paths.Add(task.file_path);
                    }
                }

                // 合併新的 file_id_mapping
                var file_id_mapping = new Dictionary<string, string>(existing_file_id_mapping);
                lock (completed_lock) {
                    foreach (var task in completed_tasks) {
                        if (!string.IsNullOrEmpty(task.knowledge_file_id)) {
                            file_id_mapping[task.file_path] = task.knowledge_file_id;
                        }
                    }
                }

                var checkpoint_data = new Dictionary<string, object> {
                    {"timestamp", DateTime.Now.ToString("o")},
                    {"completed_files", existing_completed.ToList()},
                    {"file_id_mapping", file_id_mapping},
                    {"failed_files", existing_failed.Select(t => new List<string> { t.Item1, t.Item2 }).ToList()},
                    {"pending_files", tasks_queue.Select(t => t.file_path).ToList()}
                };

                var checkpointJson = JsonSerializer.Serialize(checkpoint_data, new JsonSerializerOptions { WriteIndented = true });
                File.WriteAllText(checkpoint_file, checkpointJson);

                int total_completed = existing_completed.Count;
                // 只在整百時顯示日誌，減少輸出
                if (total_completed % 100 == 0) {
                    LogInfo($"Checkpoint saved with {total_completed} total completed files");
                }
            }
        }

        public async Task<Dictionary<string, object>> get_upload_url(HttpClient client, string file_path) {
            // 獲取預簽名上傳 URL
            var url = $"{base_url}upload-presigned-url/";

            var file_size = new FileInfo(file_path).Length;
            var filename = Path.GetFileName(file_path);

            var payload = new {
                filename = filename,
                modelName = "chatbot-file",  // 知識庫檔案使用 chatbot-file
                fieldName = "file",
                fileSize = file_size
            };

            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json"
            );

            var response = await client.PostAsync(url, content);
            response.EnsureSuccessStatusCode();

            var jsonString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<Dictionary<string, object>>(jsonString);
        }

        public async Task<string> upload_to_s3(HttpClient client, string file_path, Dictionary<string, object> upload_info) {
            // 上傳檔案到 S3
            var file_data = await File.ReadAllBytesAsync(file_path);

            var fields = JsonSerializer.Deserialize<Dictionary<string, string>>(
                upload_info["fields"].ToString()
            );

            var formData = new MultipartFormDataContent();
            foreach (var kvp in fields) {
                formData.Add(new StringContent(kvp.Value), kvp.Key);
            }

            var fileContent = new ByteArrayContent(file_data);
            fileContent.Headers.ContentType = new MediaTypeHeaderValue("application/octet-stream");
            formData.Add(fileContent, "file", Path.GetFileName(file_path));

            // 檢查是否有有效的上傳 URL
            if (!upload_info.ContainsKey("url")) {
                throw new Exception("Missing 'url' in upload_info response from presigned URL API. This indicates an API error.");
            }

            var upload_url = upload_info["url"].ToString();

            var response = await client.PostAsync(upload_url, formData);
            if (response.StatusCode == System.Net.HttpStatusCode.NoContent) {
                return fields["key"];
            } else {
                var error_text = await response.Content.ReadAsStringAsync();
                throw new Exception($"S3 upload failed: {response.StatusCode} - {error_text}");
            }
        }

        public async Task<List<Dictionary<string, object>>> register_file(HttpClient client, string file_key, string original_filename) {
            // 註冊檔案到知識庫
            var url = $"{base_url}knowledge-bases/{knowledge_base_id}/files/";

            var payload = new {
                files = new[] {
                    new {
                        file = file_key,
                        filename = original_filename
                    }
                }
            };

            var content = new StringContent(
                JsonSerializer.Serialize(payload),
                Encoding.UTF8,
                "application/json"
            );

            var response = await client.PostAsync(url, content);
            response.EnsureSuccessStatusCode();

            var jsonString = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<List<Dictionary<string, object>>>(jsonString);
        }

        public async Task<FileUploadTask> upload_single_file(HttpClient client, FileUploadTask task) {
            // 上傳單個檔案的完整流程
            var start_time = DateTime.Now;

            for (int retry = 0; retry < config.max_retries; retry++) {
                try {
                    task.status = UploadStatus.UPLOADING;

                    var upload_info = await get_upload_url(client, task.file_path);
                    var file_key = await upload_to_s3(client, task.file_path, upload_info);
                    var original_filename = Path.GetFileName(task.file_path);
                    var response = await register_file(client, file_key, original_filename);

                    // 從響應中提取 knowledge_file_id (響應是一個陣列)
                    if (response != null && response.Count > 0 && response[0].ContainsKey("id")) {
                        task.knowledge_file_id = response[0]["id"].ToString();
                    }

                    task.status = UploadStatus.SUCCESS;
                    task.upload_time = (DateTime.Now - start_time).TotalSeconds;

                    // 使用線程鎖來確保安全地添加到完成列表
                    lock (completed_lock) {
                        // 再次檢查是否已經在完成列表中
                        if (!completed_tasks.Any(t => t.file_path == task.file_path)) {
                            completed_tasks.Add(task);
                            save_checkpoint();
                        }
                    }

                    return task;

                } catch (Exception e) {
                    task.retry_count = retry + 1;
                    if (retry < config.max_retries - 1) {
                        await Task.Delay((int)(config.retry_delay * (retry + 1) * 1000));
                    } else {
                        task.status = UploadStatus.FAILED;
                        task.error_message = e.Message;
                        LogError($"Failed to upload {task.file_path}: {e.Message}");
                    }
                }
            }

            return task;
        }

        public async Task upload_batch_async(List<FileUploadTask> tasks) {
            // 異步批量上傳
            var semaphore = new SemaphoreSlim(config.max_concurrent_uploads);

            var handler = new HttpClientHandler();
            using (var client = new HttpClient(handler) { Timeout = TimeSpan.FromSeconds(config.timeout_seconds) }) {
                client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Api-Key", api_key);

                var upload_tasks = new List<Task<FileUploadTask>>();

                int total = tasks.Count;
                int completed = 0;

                foreach (var task in tasks) {
                    if (shutdown) {
                        break;
                    }

                    await semaphore.WaitAsync();

                    var uploadTask = Task.Run(async () => {
                        try {
                            var result = await upload_single_file(client, task);

                            // 從待處理佇列中移除已處理的任務
                            if (result.status == UploadStatus.SUCCESS) {
                                lock (completed_lock) {
                                    FileUploadTask removed;
                                    // Note: ConcurrentQueue doesn't support direct removal,
                                    // but we track completed separately
                                }
                            }

                            // 更新進度
                            Interlocked.Increment(ref completed);
                            Console.Write($"\rUploading: {completed}/{total} (Success: {completed_tasks.Count}, Failed: {failed_tasks.Count})");

                            return result;
                        } finally {
                            semaphore.Release();
                        }
                    });

                    upload_tasks.Add(uploadTask);
                }

                var results = await Task.WhenAll(upload_tasks);

                foreach (var result in results) {
                    if (result.status == UploadStatus.FAILED) {
                        failed_tasks.Add(result);
                    }
                }
            }

            Console.WriteLine();
        }

        public async Task<Dictionary<string, Dictionary<string, object>>> get_all_knowledge_files() {
            // 獲取知識庫中所有檔案的詳細資訊，返回以 id 為 key 的字典
            var all_files = new Dictionary<string, Dictionary<string, object>>();
            int page = 1;

            try {
                LogInfo("Fetching knowledge base files...");

                using (var client = new HttpClient()) {
                    client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Api-Key", api_key);
                    client.Timeout = TimeSpan.FromSeconds(30);

                    // 先獲取第一頁來了解總數
                    var url = $"{base_url}knowledge-bases/{knowledge_base_id}/files/?page=1&page_size=100";
                    var response = await client.GetAsync(url);
                    response.EnsureSuccessStatusCode();

                    var jsonString = await response.Content.ReadAsStringAsync();
                    var first_page = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(jsonString);

                    // 估算總頁數
                    int total_count = 0;
                    if (first_page.ContainsKey("count")) {
                        total_count = first_page["count"].GetInt32();
                    }

                    var results = new List<Dictionary<string, object>>();
                    if (first_page.ContainsKey("results")) {
                        results = JsonSerializer.Deserialize<List<Dictionary<string, object>>>(
                            first_page["results"].GetRawText()
                        );
                    }

                    int per_page = results.Count;
                    int estimated_pages = per_page > 0 ? (total_count / per_page) + (total_count % per_page > 0 ? 1 : 0) : 1;

                    LogInfo($"Estimated {total_count} files across {estimated_pages} pages");

                    // 處理第一頁
                    foreach (var file in results) {
                        if (file.ContainsKey("id")) {
                            var file_id = file["id"].ToString();
                            var filename = file.ContainsKey("filename") ? file["filename"].ToString() : "";

                            var created_at = "";
                            if (file.ContainsKey("createdAt")) {
                                var createdAtValue = file["createdAt"].ToString();
                                if (long.TryParse(createdAtValue, out long timestamp)) {
                                    created_at = DateTimeOffset.FromUnixTimeMilliseconds(timestamp).ToString("o");
                                }
                            }

                            all_files[file_id] = new Dictionary<string, object> {
                                {"id", file_id},
                                {"filename", filename},
                                {"created_at", created_at},
                                {"status", file.ContainsKey("status") ? file["status"].ToString() : ""}
                            };
                        }
                    }

                    Console.Write($"\rFetching KB pages: 1/{estimated_pages}");

                    // 處理後續頁面
                    page = 2;
                    bool has_next = first_page.ContainsKey("next") && !first_page["next"].ToString().Equals("null");

                    while (has_next) {
                        url = $"{base_url}knowledge-bases/{knowledge_base_id}/files/?page={page}&page_size=100";
                        response = await client.GetAsync(url);
                        response.EnsureSuccessStatusCode();

                        jsonString = await response.Content.ReadAsStringAsync();
                        var data = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(jsonString);

                        if (data.ContainsKey("results")) {
                            results = JsonSerializer.Deserialize<List<Dictionary<string, object>>>(
                                data["results"].GetRawText()
                            );

                            foreach (var file in results) {
                                if (file.ContainsKey("id")) {
                                    var file_id = file["id"].ToString();
                                    var filename = file.ContainsKey("filename") ? file["filename"].ToString() : "";

                                    var created_at = "";
                                    if (file.ContainsKey("createdAt")) {
                                        var createdAtValue = file["createdAt"].ToString();
                                        if (long.TryParse(createdAtValue, out long timestamp)) {
                                            created_at = DateTimeOffset.FromUnixTimeMilliseconds(timestamp).ToString("o");
                                        }
                                    }

                                    all_files[file_id] = new Dictionary<string, object> {
                                        {"id", file_id},
                                        {"filename", filename},
                                        {"created_at", created_at},
                                        {"status", file.ContainsKey("status") ? file["status"].ToString() : ""}
                                    };
                                }
                            }
                        }

                        Console.Write($"\rFetching KB pages: {page}/{estimated_pages}");

                        has_next = data.ContainsKey("next") && !data["next"].ToString().Equals("null");
                        page++;
                    }

                    Console.WriteLine();
                }

                LogInfo($"Successfully fetched {all_files.Count} files from knowledge base");
                return all_files;

            } catch (Exception e) {
                LogError($"Failed to get knowledge base files: {e.Message}");
                return all_files;
            }
        }

        public async Task check_upload_integrity() {
            // 檢查上傳完整性，識別重複和漏傳的檔案
            LogInfo("Checking upload integrity...");

            // 獲取知識庫中所有檔案 (以 ID 為 key)
            var kb_files = await get_all_knowledge_files();
            var kb_file_ids = new HashSet<string>(kb_files.Keys);

            // 從 checkpoint 載入所有已上傳的檔案
            var checkpoint = load_checkpoint();
            if (checkpoint == null) {
                LogWarning("No checkpoint found for integrity check");
                return;
            }

            var uploaded_files = new HashSet<string>();
            if (checkpoint.ContainsKey("completed_files")) {
                var completed_list = JsonSerializer.Deserialize<List<string>>(
                    checkpoint["completed_files"].ToString()
                );
                uploaded_files = new HashSet<string>(completed_list);
            }

            var file_id_mapping = new Dictionary<string, string>();
            if (checkpoint.ContainsKey("file_id_mapping")) {
                file_id_mapping = JsonSerializer.Deserialize<Dictionary<string, string>>(
                    checkpoint["file_id_mapping"].ToString()
                );
            }

            // 從 checkpoint 中獲取所有上傳的 file IDs
            var uploaded_file_ids = new HashSet<string>(file_id_mapping.Values);

            // 檢查漏傳（在 checkpoint 但不在知識庫中的 ID）
            var missing_ids = new HashSet<string>(uploaded_file_ids);
            missing_ids.ExceptWith(kb_file_ids);

            var missing_files = new List<Dictionary<string, string>>();
            foreach (var kvp in file_id_mapping) {
                if (missing_ids.Contains(kvp.Value)) {
                    missing_files.Add(new Dictionary<string, string> {
                        {"filename", Path.GetFileName(kvp.Key)},
                        {"filepath", kvp.Key},
                        {"knowledge_file_id", kvp.Value}
                    });
                }
            }

            // 檢查額外檔案（在知識庫但不在 checkpoint 記錄中）
            var extra_ids = new HashSet<string>(kb_file_ids);
            extra_ids.ExceptWith(uploaded_file_ids);

            var extra_files = new List<Dictionary<string, string>>();
            foreach (var file_id in extra_ids) {
                if (kb_files.ContainsKey(file_id)) {
                    extra_files.Add(new Dictionary<string, string> {
                        {"filename", kb_files[file_id]["filename"].ToString()},
                        {"knowledge_file_id", file_id},
                        {"created_at", kb_files[file_id]["created_at"].ToString()}
                    });
                }
            }

            // 輸出結果
            if (missing_files.Count > 0) {
                LogWarning($"Found {missing_files.Count} missing files (uploaded but not in KB):");
                LogWarning("These files may have been uploaded but later deleted by user, or upload failed:");
                for (int i = 0; i < Math.Min(10, missing_files.Count); i++) {
                    var file = missing_files[i];
                    LogWarning($"  - {file["filename"]} (ID: {file["knowledge_file_id"]})");
                }
                if (missing_files.Count > 10) {
                    LogWarning($"  ... and {missing_files.Count - 10} more missing files");
                }
            }

            if (extra_files.Count > 0) {
                LogInfo($"Found {extra_files.Count} extra files in KB (not in upload records):");
                LogInfo("These files may be duplicates or uploaded by other methods:");
                for (int i = 0; i < Math.Min(10, extra_files.Count); i++) {
                    var file = extra_files[i];
                    LogInfo($"  - {file["filename"]} (ID: {file["knowledge_file_id"]})");
                }
            }

            // 儲存完整性檢查報告
            var integrity_report = new Dictionary<string, object> {
                {"timestamp", DateTime.Now.ToString("o")},
                {"summary", new Dictionary<string, int> {
                    {"total_kb_files", kb_files.Count},
                    {"total_uploaded_files", uploaded_files.Count},
                    {"total_uploaded_ids", uploaded_file_ids.Count},
                    {"missing", missing_files.Count},
                    {"extra", extra_files.Count}
                }},
                {"missing_files", missing_files},
                {"extra_files", extra_files}
            };

            var report_file = Path.Combine(report_dir, $"integrity_check_{DateTime.Now:yyyyMMdd_HHmmss}.json");
            var jsonString = JsonSerializer.Serialize(integrity_report, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(report_file, jsonString);

            LogInfo($"Integrity check report saved to {report_file}");
        }

        public async Task run_upload(string directory) {
            // 執行批量上傳主流程
            // 如果初始化時沒有設定來源目錄，在這裡更新
            if (string.IsNullOrEmpty(source_directory)) {
                source_directory = directory;
                // 重新設定輸出目錄
                var folder_name = Path.GetFileName(Path.GetFullPath(directory).TrimEnd(Path.DirectorySeparatorChar));
                var unique_dir_name = $"{folder_name}_{knowledge_base_id.Substring(0, Math.Min(8, knowledge_base_id.Length))}";
                var program_dir = Path.GetDirectoryName(System.Reflection.Assembly.GetExecutingAssembly().Location);
                output_dir = Path.Combine(program_dir, "upload_outputs", unique_dir_name);
                checkpoint_dir = Path.Combine(output_dir, "checkpoints");
                log_dir = Path.Combine(output_dir, "logs");
                report_dir = Path.Combine(output_dir, "reports");
                Directory.CreateDirectory(checkpoint_dir);
                Directory.CreateDirectory(log_dir);
                Directory.CreateDirectory(report_dir);
                // 更新 checkpoint 檔案路徑
                checkpoint_file = Path.Combine(checkpoint_dir, "upload_checkpoint.json");
            }

            LogInfo($"Scanning directory: {directory}");
            LogInfo($"Output directory: {output_dir}");

            var all_tasks = scan_files(directory);

            var checkpoint = load_checkpoint();
            if (checkpoint != null) {
                LogInfo("Found checkpoint, resuming upload...");
                var completed_files = new HashSet<string>();
                if (checkpoint.ContainsKey("completed_files")) {
                    var completed_list = JsonSerializer.Deserialize<List<string>>(
                        checkpoint["completed_files"].ToString()
                    );
                    completed_files = new HashSet<string>(completed_list);
                }
                all_tasks = all_tasks.Where(task => !completed_files.Contains(task.file_path)).ToList();
            }

            int total_files = all_tasks.Count;
            LogInfo($"Found {total_files} files to upload");

            if (total_files == 0) {
                LogInfo("No files to upload");
                return;
            }

            foreach (var task in all_tasks) {
                tasks_queue.Enqueue(task);
            }

            if (!shutdown) {
                await upload_batch_async(all_tasks);
            }

            Console.WriteLine();
            LogInfo("Upload process completed");
            LogInfo($"Total files: {total_files}");
            LogInfo($"Successfully uploaded: {completed_tasks.Count}");
            LogInfo($"Failed uploads: {failed_tasks.Count}");

            // 在上傳完成後進行檔案比對
            await check_upload_integrity();

            save_final_report();
        }

        public void save_final_report() {
            // 儲存最終上傳報告
            var avg_time = completed_tasks.Count > 0
                ? completed_tasks.Where(t => t.upload_time.HasValue).Average(t => t.upload_time.Value)
                : 0;

            var report = new Dictionary<string, object> {
                {"summary", new Dictionary<string, object> {
                    {"total_files", completed_tasks.Count + failed_tasks.Count},
                    {"successful_uploads", completed_tasks.Count},
                    {"failed_uploads", failed_tasks.Count},
                    {"average_upload_time", avg_time}
                }},
                {"successful_files", completed_tasks.Select(task => new Dictionary<string, object> {
                    {"file_path", task.file_path},
                    {"file_size", task.file_size},
                    {"upload_time", task.upload_time}
                }).ToList()},
                {"failed_files", failed_tasks.Select(task => new Dictionary<string, object> {
                    {"file_path", task.file_path},
                    {"error", task.error_message},
                    {"retry_count", task.retry_count}
                }).ToList()}
            };

            var report_file = Path.Combine(report_dir, $"upload_report_{DateTime.Now:yyyyMMdd_HHmmss}.json");
            var jsonString = JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(report_file, jsonString);

            LogInfo($"Final report saved to {report_file}");
        }

        public void Dispose() {
            log_writer?.Close();
        }
    }

    public static async Task Main() {
        Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
        Debug.Assert(KNOWLEDGE_BASE_ID != "<your-knowledge-base-id>", "Please set your knowledge base id");
        Debug.Assert(FILES_DIRECTORY != "<your-files-directory>", "Please set your files directory");

        var config = new UploadConfig {
            max_concurrent_uploads = 10,
            max_retries = 3,
            retry_delay = 2.0,
            timeout_seconds = 300
        };

        var uploader = new BatchFileUploaderAdvanced(API_KEY, KNOWLEDGE_BASE_ID, config, sourceDirectory: FILES_DIRECTORY);
        await uploader.run_upload(FILES_DIRECTORY);
        uploader.Dispose();
    }
}
