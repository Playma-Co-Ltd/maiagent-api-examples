
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using System.Diagnostics;
using Utils;

public static class fix_failed_files {

    // Configuration - Replace with your actual values
    public static string API_KEY = "<your-api-key>";
    public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>";   // 你的知識庫 ID
    public static string FILES_DIRECTORY = "<your-files-directory>";    // 你要上傳的檔案目錄
    public static string STATUS_REPORT_PATH = "<path-to-your-status-report>";  // Path to status scan report, e.g., 'status_scan_20250801_124703.json'

    public class FailedFilesFixer {
        private string api_key;
        private string knowledge_base_id;
        private string files_directory;
        private MaiAgentHelper maiagent_helper;
        private string base_url = "https://api.maiagent.ai/api/v1/";

        // Results tracking
        public List<Dictionary<string, object>> deleted_files = new List<Dictionary<string, object>>();
        public List<Dictionary<string, object>> failed_deletions = new List<Dictionary<string, object>>();
        public List<Dictionary<string, object>> successful_uploads = new List<Dictionary<string, object>>();
        public List<Dictionary<string, object>> failed_uploads = new List<Dictionary<string, object>>();

        public FailedFilesFixer(string apiKey, string knowledgeBaseId, string filesDirectory) {
            this.api_key = apiKey;
            this.knowledge_base_id = knowledgeBaseId;
            this.files_directory = filesDirectory;
            this.maiagent_helper = new MaiAgentHelper(apiKey);
        }

        public List<Dictionary<string, object>> load_failed_files(string status_report_path) {
            // Load failed files from status scan report
            if (!File.Exists(status_report_path)) {
                Console.WriteLine($"❌ Status report not found: {status_report_path}");
                return new List<Dictionary<string, object>>();
            }

            try {
                var jsonString = File.ReadAllText(status_report_path);
                var data = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(jsonString);

                if (data.ContainsKey("failed_files")) {
                    var failed_files = JsonSerializer.Deserialize<List<Dictionary<string, object>>>(
                        data["failed_files"].GetRawText()
                    );
                    Console.WriteLine($"📋 Found {failed_files.Count} failed files in status report");
                    return failed_files;
                }

                return new List<Dictionary<string, object>>();

            } catch (Exception e) {
                Console.WriteLine($"❌ Error reading status report: {e.Message}");
                return new List<Dictionary<string, object>>();
            }
        }

        public List<Dictionary<string, object>> delete_failed_files(List<Dictionary<string, object>> failed_files) {
            // Delete failed files from knowledge base
            if (failed_files.Count == 0) {
                return new List<Dictionary<string, object>>();
            }

            Console.WriteLine(new string('=', 60));
            Console.WriteLine("Deleting Failed Files");
            Console.WriteLine(new string('=', 60));

            // Show files to be deleted
            for (int i = 0; i < Math.Min(10, failed_files.Count); i++) {
                var file = failed_files[i];
                var filename = file.ContainsKey("filename") ? file["filename"].ToString() : "Unknown";
                var file_id = file.ContainsKey("id") ? file["id"].ToString() : "Unknown";
                Console.WriteLine($"{i + 1}. {filename} (ID: {file_id})");
            }

            if (failed_files.Count > 10) {
                Console.WriteLine($"... and {failed_files.Count - 10} more files");
            }

            Console.WriteLine("\n" + new string('=', 60));
            Console.Write("⚠️  Delete these failed files? Type 'YES' to confirm: ");
            var confirm = Console.ReadLine();
            if (confirm != "YES") {
                Console.WriteLine("❌ Deletion cancelled");
                return new List<Dictionary<string, object>>();
            }

            Console.WriteLine("\n🗑️  Deleting failed files...");

            for (int i = 0; i < failed_files.Count; i++) {
                try {
                    var file = failed_files[i];
                    var file_id = file["id"].ToString();
                    var filename = file["filename"].ToString();

                    maiagent_helper.delete_knowledge_file(knowledge_base_id, file_id);
                    deleted_files.Add(file);
                    Console.WriteLine($"✓ Deleted: {filename}");

                    if ((i + 1) % 10 == 0) {
                        Console.WriteLine($"   Progress: {i + 1}/{failed_files.Count}");
                    }

                    Thread.Sleep(300);  // Rate limiting

                } catch (Exception e) {
                    var file = failed_files[i];
                    var filename = file["filename"].ToString();

                    // Handle API returning 500 but deletion actually succeeding
                    if (e.Message.Contains("500") || e.Message.Contains("Internal Server Error")) {
                        deleted_files.Add(file);
                        Console.WriteLine($"✓ Deleted: {filename} (API returned 500 but likely successful)");
                    } else {
                        failed_deletions.Add(new Dictionary<string, object> {
                            {"file", file},
                            {"error", e.Message}
                        });
                        Console.WriteLine($"❌ Failed to delete: {filename} - {e.Message}");
                    }
                }
            }

            Console.WriteLine($"\n✅ Deletion completed: {deleted_files.Count} deleted, {failed_deletions.Count} failed");
            return deleted_files;
        }

        public async Task<Dictionary<string, object>> get_upload_url(HttpClient client, string file_path) {
            // Get presigned upload URL
            var url = $"{base_url}upload-presigned-url/";

            var file_size = new FileInfo(file_path).Length;
            var filename = Path.GetFileName(file_path);

            var payload = new {
                filename = filename,
                modelName = "chatbot-file",
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
            // Upload file to S3
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
            // Register file to knowledge base
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

        public async Task<bool> upload_single_file(HttpClient client, string file_path) {
            // Upload a single file
            try {
                var upload_info = await get_upload_url(client, file_path);
                var file_key = await upload_to_s3(client, file_path, upload_info);
                var original_filename = Path.GetFileName(file_path);
                var response = await register_file(client, file_key, original_filename);

                // Extract new file ID
                string new_file_id = null;
                if (response != null && response.Count > 0 && response[0].ContainsKey("id")) {
                    new_file_id = response[0]["id"].ToString();
                }

                successful_uploads.Add(new Dictionary<string, object> {
                    {"file_path", file_path},
                    {"filename", original_filename},
                    {"new_file_id", new_file_id},
                    {"upload_time", DateTime.Now.ToString("o")}
                });

                return true;

            } catch (Exception e) {
                failed_uploads.Add(new Dictionary<string, object> {
                    {"file_path", file_path},
                    {"filename", Path.GetFileName(file_path)},
                    {"error", e.Message},
                    {"upload_time", DateTime.Now.ToString("o")}
                });
                return false;
            }
        }

        public async Task reupload_files(List<Dictionary<string, object>> deleted_files) {
            // Re-upload the deleted files
            if (deleted_files.Count == 0) {
                return;
            }

            Console.WriteLine(new string('=', 60));
            Console.WriteLine("Re-uploading Files");
            Console.WriteLine(new string('=', 60));

            // Find files that exist in the directory
            var files_to_upload = new List<string>();
            var missing_files = new List<string>();

            foreach (var file in deleted_files) {
                var filename = file["filename"].ToString();
                var file_path = Path.Combine(files_directory, filename);

                if (File.Exists(file_path)) {
                    files_to_upload.Add(file_path);
                } else {
                    missing_files.Add(filename);
                }
            }

            Console.WriteLine($"📁 Files to re-upload: {files_to_upload.Count}");
            Console.WriteLine($"❌ Missing files: {missing_files.Count}");

            if (missing_files.Count > 0) {
                Console.WriteLine($"\nMissing files (cannot re-upload):");
                for (int i = 0; i < Math.Min(5, missing_files.Count); i++) {
                    Console.WriteLine($"  - {missing_files[i]}");
                }
                if (missing_files.Count > 5) {
                    Console.WriteLine($"  ... and {missing_files.Count - 5} more");
                }
            }

            if (files_to_upload.Count == 0) {
                Console.WriteLine("❌ No files available for re-upload");
                return;
            }

            Console.WriteLine($"\n🔄 Starting re-upload of {files_to_upload.Count} files...");

            // Upload files
            var handler = new HttpClientHandler();
            using (var client = new HttpClient(handler) { Timeout = TimeSpan.FromMinutes(5) }) {
                client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Api-Key", api_key);

                int completed = 0;
                foreach (var file_path in files_to_upload) {
                    var success = await upload_single_file(client, file_path);
                    completed++;

                    Console.Write($"\rRe-uploading: {completed}/{files_to_upload.Count} (Success: {successful_uploads.Count}, Failed: {failed_uploads.Count})");

                    await Task.Delay(100);
                }

                Console.WriteLine();
            }
        }

        public string save_results() {
            // Save operation results to log file
            var results = new Dictionary<string, object> {
                {"timestamp", DateTime.Now.ToString("o")},
                {"knowledge_base_id", knowledge_base_id},
                {"files_directory", files_directory},
                {"status_report_used", STATUS_REPORT_PATH},
                {"summary", new Dictionary<string, int> {
                    {"deleted_files", deleted_files.Count},
                    {"failed_deletions", failed_deletions.Count},
                    {"successful_uploads", successful_uploads.Count},
                    {"failed_uploads", failed_uploads.Count}
                }},
                {"deleted_files", deleted_files},
                {"failed_deletions", failed_deletions},
                {"successful_uploads", successful_uploads},
                {"failed_uploads", failed_uploads}
            };

            var log_filename = $"fix_failed_files_log_{DateTime.Now:yyyyMMdd_HHmmss}.json";
            var jsonString = JsonSerializer.Serialize(results, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(log_filename, jsonString);

            return log_filename;
        }
    }

    public static async Task Main() {
        // Fix failed files in knowledge base
        //
        // This script will:
        // 1. Read a status scan report to identify failed files
        // 2. Delete the failed files from the knowledge base
        // 3. Re-upload the files from the local directory
        // 4. Save a detailed log of all operations
        //
        // Usage:
        // 1. Set your API_KEY, KNOWLEDGE_BASE_ID, FILES_DIRECTORY, and STATUS_REPORT_PATH
        // 2. Make sure you have a status scan report with failed files
        // 3. Ensure the original files exist in FILES_DIRECTORY
        // 4. Run the program

        Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
        Debug.Assert(KNOWLEDGE_BASE_ID != "<your-knowledge-base-id>", "Please set your knowledge base id");
        Debug.Assert(FILES_DIRECTORY != "<your-files-directory>", "Please set your files directory");
        Debug.Assert(STATUS_REPORT_PATH != "<path-to-your-status-report>", "Please set the path to your status scan report");

        Console.WriteLine("Failed Files Fixer");
        Console.WriteLine("==================");
        Console.WriteLine($"Knowledge Base: {KNOWLEDGE_BASE_ID}");
        Console.WriteLine($"Files Directory: {FILES_DIRECTORY}");
        Console.WriteLine($"Status Report: {STATUS_REPORT_PATH}");
        Console.WriteLine();

        var fixer = new FailedFilesFixer(API_KEY, KNOWLEDGE_BASE_ID, FILES_DIRECTORY);

        // Load failed files
        var failed_files = fixer.load_failed_files(STATUS_REPORT_PATH);
        if (failed_files.Count == 0) {
            Console.WriteLine("✅ No failed files found!");
            return;
        }

        // Delete failed files
        var deleted_files = fixer.delete_failed_files(failed_files);
        if (deleted_files.Count == 0) {
            Console.WriteLine("❌ No files were deleted, stopping...");
            return;
        }

        // Re-upload files
        await fixer.reupload_files(deleted_files);

        // Save results and show summary
        var log_file = fixer.save_results();

        Console.WriteLine("\n" + new string('=', 60));
        Console.WriteLine("Operation Summary:");
        Console.WriteLine(new string('=', 60));
        Console.WriteLine($"🗑️  Files deleted: {fixer.deleted_files.Count}");
        Console.WriteLine($"❌ Delete failures: {fixer.failed_deletions.Count}");
        Console.WriteLine($"✅ Files re-uploaded: {fixer.successful_uploads.Count}");
        Console.WriteLine($"❌ Upload failures: {fixer.failed_uploads.Count}");
        Console.WriteLine($"📄 Log saved to: {log_file}");

        if (fixer.failed_uploads.Count > 0) {
            Console.WriteLine($"\nUpload failures:");
            for (int i = 0; i < Math.Min(3, fixer.failed_uploads.Count); i++) {
                var failed = fixer.failed_uploads[i];
                Console.WriteLine($"  - {failed["filename"]}: {failed["error"]}");
            }
        }
    }
}
