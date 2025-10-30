
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Diagnostics;

public static class upload_missing_files {

    // Configuration - Replace with your actual values
    public static string API_KEY = "<your-api-key>";
    public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>";   // 你的知識庫 ID
    public static string FILES_DIRECTORY = "<your-files-directory>";    // 你要上傳的檔案目錄
    public static string INTEGRITY_REPORT_PATH = "<path-to-your-integrity-check-report>";  // Path to integrity check report, e.g., 'upload_outputs/json_files_4e9ffa82/reports/....json'

    public class MissingFilesUploader {
        private string api_key;
        private string knowledge_base_id;
        private string files_directory;
        private string base_url = "https://api.maiagent.ai/api/v1/";

        // Results tracking
        public List<Dictionary<string, object>> successful_uploads = new List<Dictionary<string, object>>();
        public List<Dictionary<string, object>> failed_uploads = new List<Dictionary<string, object>>();

        public MissingFilesUploader(string apiKey, string knowledgeBaseId, string filesDirectory) {
            this.api_key = apiKey;
            this.knowledge_base_id = knowledgeBaseId;
            this.files_directory = filesDirectory;
        }

        public List<Dictionary<string, object>> load_missing_files(string integrity_report_path) {
            // Load missing files from an integrity check report
            //
            // Args:
            //     integrity_report_path: Path to the integrity check JSON file
            //
            // Returns:
            //     List of missing files to upload

            if (!File.Exists(integrity_report_path)) {
                Console.WriteLine($"❌ Integrity report not found: {integrity_report_path}");
                Console.WriteLine("Please check the file path and make sure the integrity check report exists.");
                return new List<Dictionary<string, object>>();
            }

            try {
                var jsonString = File.ReadAllText(integrity_report_path);
                var data = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(jsonString);

                // Look for missing_files (files in upload records but not in KB)
                if (data.ContainsKey("missing_files")) {
                    var missing_files = JsonSerializer.Deserialize<List<Dictionary<string, object>>>(
                        data["missing_files"].GetRawText()
                    );

                    if (missing_files.Count > 0) {
                        Console.WriteLine($"📋 Found {missing_files.Count} missing files in integrity report");
                        return missing_files;
                    } else {
                        Console.WriteLine("✅ No missing files found in the report");
                        return new List<Dictionary<string, object>>();
                    }
                }

                Console.WriteLine("✅ No missing files found in the report");
                return new List<Dictionary<string, object>>();

            } catch (Exception e) {
                Console.WriteLine($"❌ Error reading integrity report: {e.Message}");
                return new List<Dictionary<string, object>>();
            }
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

        public async Task upload_missing_files(List<Dictionary<string, object>> missing_files) {
            // Upload missing files to knowledge base
            //
            // Args:
            //     missing_files: List of missing file info dicts with 'filename' and 'filepath'

            if (missing_files.Count == 0) {
                Console.WriteLine("❌ No files to upload");
                return;
            }

            Console.WriteLine(new string('=', 60));
            Console.WriteLine("Files to be uploaded:");
            Console.WriteLine(new string('=', 60));

            // Check which files exist and prepare upload list
            var files_to_upload = new List<string>();
            var files_not_found = new List<string>();

            foreach (var file in missing_files) {
                var filename = file.ContainsKey("filename") ? file["filename"].ToString() : "Unknown";
                var filepath = file.ContainsKey("filepath") ? file["filepath"].ToString() : "";

                // Try both the filepath from report and files_directory + filename
                var possible_paths = new List<string> {
                    filepath,
                    Path.Combine(files_directory, filename)
                };

                bool file_found = false;
                foreach (var path in possible_paths) {
                    if (!string.IsNullOrEmpty(path) && File.Exists(path)) {
                        files_to_upload.Add(path);
                        Console.WriteLine($"✓ Found: {filename}");
                        file_found = true;
                        break;
                    }
                }

                if (!file_found) {
                    files_not_found.Add(filename);
                    Console.WriteLine($"❌ Not found: {filename}");
                }
            }

            Console.WriteLine("\n" + new string('=', 50));
            Console.WriteLine($"📁 Files ready to upload: {files_to_upload.Count}");
            Console.WriteLine($"❌ Files not found: {files_not_found.Count}");

            if (files_not_found.Count > 0) {
                Console.WriteLine($"\nFiles not found in directory:");
                for (int i = 0; i < Math.Min(5, files_not_found.Count); i++) {
                    Console.WriteLine($"  - {files_not_found[i]}");
                }
                if (files_not_found.Count > 5) {
                    Console.WriteLine($"  ... and {files_not_found.Count - 5} more");
                }
            }

            if (files_to_upload.Count == 0) {
                Console.WriteLine("❌ No files available for upload");
                return;
            }

            Console.WriteLine("\n" + new string('=', 60));
            Console.Write("⚠️  Upload these missing files? Type 'YES' to confirm: ");
            var confirm = Console.ReadLine();
            if (confirm != "YES") {
                Console.WriteLine("❌ Upload cancelled");
                return;
            }

            // Perform upload
            Console.WriteLine($"\n📤 Starting upload of {files_to_upload.Count} files...");

            var handler = new HttpClientHandler();
            using (var client = new HttpClient(handler) { Timeout = TimeSpan.FromMinutes(5) }) {
                client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Api-Key", api_key);

                int completed = 0;
                foreach (var file_path in files_to_upload) {
                    var success = await upload_single_file(client, file_path);
                    completed++;

                    Console.Write($"\rUploading: {completed}/{files_to_upload.Count} (Success: {successful_uploads.Count}, Failed: {failed_uploads.Count})");

                    // Rate limiting
                    await Task.Delay(100);
                }

                Console.WriteLine();
            }

            // Save upload results
            _save_upload_results();
        }

        private string _save_upload_results() {
            // Save upload results to log file
            var results = new Dictionary<string, object> {
                {"timestamp", DateTime.Now.ToString("o")},
                {"knowledge_base_id", knowledge_base_id},
                {"files_directory", files_directory},
                {"integrity_report_used", INTEGRITY_REPORT_PATH},
                {"total_files", successful_uploads.Count + failed_uploads.Count},
                {"successful_uploads", successful_uploads.Count},
                {"failed_uploads", failed_uploads.Count},
                {"successful_uploads_details", successful_uploads},
                {"failed_uploads_details", failed_uploads}
            };

            var log_filename = $"missing_files_upload_{DateTime.Now:yyyyMMdd_HHmmss}.json";
            var jsonString = JsonSerializer.Serialize(results, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(log_filename, jsonString);

            Console.WriteLine($"\n📄 Upload log saved to: {log_filename}");
            return log_filename;
        }
    }

    public static async Task Main() {
        // Upload missing files to knowledge base
        //
        // This script is designed to upload files that are missing from the knowledge base
        // based on an integrity check report.
        //
        // Usage:
        // 1. Set your API_KEY, KNOWLEDGE_BASE_ID, FILES_DIRECTORY, and INTEGRITY_REPORT_PATH
        // 2. Make sure you have an integrity check report with missing_files
        // 3. Ensure the missing files exist in FILES_DIRECTORY
        // 4. Run the program
        //
        // The script will:
        // - Read the integrity check report from the specified path
        // - Check which missing files exist in your local directory
        // - Show you which files will be uploaded
        // - Ask for confirmation before upload
        // - Save a detailed log of the upload process
        //
        // Note: The integrity check report should contain 'missing_files' - these are files
        // that were supposed to be uploaded but are missing from the knowledge base.

        Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
        Debug.Assert(KNOWLEDGE_BASE_ID != "<your-knowledge-base-id>", "Please set your knowledge base id");
        Debug.Assert(FILES_DIRECTORY != "<your-files-directory>", "Please set your files directory");
        Debug.Assert(INTEGRITY_REPORT_PATH != "<path-to-your-integrity-check-report>", "Please set the path to your integrity check report");

        Console.WriteLine("Missing Files Uploader");
        Console.WriteLine("=====================");
        Console.WriteLine($"Knowledge Base: {KNOWLEDGE_BASE_ID}");
        Console.WriteLine($"Files Directory: {FILES_DIRECTORY}");
        Console.WriteLine($"Integrity Report: {INTEGRITY_REPORT_PATH}");
        Console.WriteLine();

        var uploader = new MissingFilesUploader(API_KEY, KNOWLEDGE_BASE_ID, FILES_DIRECTORY);

        // Load missing files from integrity report
        var missing_files = uploader.load_missing_files(INTEGRITY_REPORT_PATH);

        if (missing_files.Count > 0) {
            await uploader.upload_missing_files(missing_files);

            // Show summary
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("Upload Summary:");
            Console.WriteLine(new string('=', 60));
            Console.WriteLine($"✅ Successfully uploaded: {uploader.successful_uploads.Count} files");
            Console.WriteLine($"❌ Failed uploads: {uploader.failed_uploads.Count} files");

            if (uploader.failed_uploads.Count > 0) {
                Console.WriteLine($"\nUpload failures:");
                for (int i = 0; i < Math.Min(5, uploader.failed_uploads.Count); i++) {
                    var failed = uploader.failed_uploads[i];
                    Console.WriteLine($"  - {failed["filename"]}: {failed["error"]}");
                }
            }
        } else {
            Console.WriteLine("✅ No missing files to upload!");
        }
    }
}
