
using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Diagnostics;

public static class scan_file_status {

    // Configuration - Replace with your actual values
    public static string API_KEY = "<your-api-key>";
    public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>";   // 你的知識庫 ID
    public static string BASE_URL = "https://api.maiagent.ai/api/v1/";

    public class KnowledgeBaseStatusScanner {
        private string api_key;
        private string knowledge_base_id;
        private string base_url;

        public KnowledgeBaseStatusScanner(string apiKey, string knowledgeBaseId, string baseUrl = null) {
            this.api_key = apiKey;
            this.knowledge_base_id = knowledgeBaseId;
            this.base_url = baseUrl ?? BASE_URL;
        }

        public (Dictionary<string, List<Dictionary<string, object>>>, string) scan_files_by_status(int? max_pages = null, int page_size = 100) {
            // Scan knowledge base files and categorize by status
            //
            // Args:
            //     max_pages: Maximum number of pages to scan (null for all pages)
            //     page_size: Number of files per page (default: 100)

            using (var client = new HttpClient()) {
                client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Api-Key", api_key);

                Console.WriteLine(new string('=', 60));
                Console.WriteLine("Knowledge Base File Status Scanner");
                Console.WriteLine(new string('=', 60));

                // Status counters
                var status_count = new Dictionary<string, List<Dictionary<string, object>>> {
                    {"initial", new List<Dictionary<string, object>>()},
                    {"processing", new List<Dictionary<string, object>>()},
                    {"done", new List<Dictionary<string, object>>()},
                    {"failed", new List<Dictionary<string, object>>()},
                    {"other", new List<Dictionary<string, object>>()}
                };

                int page = 1;
                int total_scanned = 0;

                // Get total count from first page
                var url = $"{base_url}knowledge-bases/{knowledge_base_id}/files/?page=1&page_size={page_size}";
                var response = client.GetAsync(url).Result;
                response.EnsureSuccessStatusCode();
                var jsonString = response.Content.ReadAsStringAsync().Result;
                var data = JsonSerializer.Deserialize<Dictionary<string, object>>(jsonString);

                int total_count = data.ContainsKey("count") ? Convert.ToInt32(data["count"]) : 0;
                var results = data.ContainsKey("results") ? (JsonElement)data["results"] : new JsonElement();
                int per_page = results.GetArrayLength();
                int total_pages = per_page > 0 ? (total_count / per_page) + (total_count % per_page > 0 ? 1 : 0) : 1;

                int scan_pages = Math.Min(max_pages ?? total_pages, total_pages);

                Console.WriteLine($"Knowledge Base ID: {knowledge_base_id}");
                Console.WriteLine($"Total files: {total_count:N0}");
                Console.WriteLine($"Total pages: {total_pages:N0}");
                if (max_pages.HasValue) {
                    Console.WriteLine($"Will scan: {scan_pages:N0} pages (limited)");
                } else {
                    Console.WriteLine($"Will scan: {scan_pages:N0} pages (all)");
                }
                Console.WriteLine();

                while (page <= scan_pages) {
                    try {
                        url = $"{base_url}knowledge-bases/{knowledge_base_id}/files/?page={page}&page_size={page_size}";
                        response = client.GetAsync(url).Result;
                        response.EnsureSuccessStatusCode();
                        jsonString = response.Content.ReadAsStringAsync().Result;
                        data = JsonSerializer.Deserialize<Dictionary<string, object>>(jsonString);

                        if (data.ContainsKey("results")) {
                            var filesArray = (JsonElement)data["results"];
                            foreach (var file in filesArray.EnumerateArray()) {
                                var status = file.GetProperty("status").GetString() ?? "unknown";
                                var file_info = new Dictionary<string, object> {
                                    {"id", file.GetProperty("id").GetString()},
                                    {"filename", file.GetProperty("filename").GetString()},
                                    {"status", status},
                                    {"created_at", file.TryGetProperty("createdAt", out var createdAt) ? createdAt.ToString() : null}
                                };

                                if (status_count.ContainsKey(status)) {
                                    status_count[status].Add(file_info);
                                } else {
                                    status_count["other"].Add(file_info);
                                }

                                total_scanned++;
                            }
                        }

                        Console.Write($"\rScanning page {page}/{scan_pages}...");

                        if (!data.ContainsKey("next") || data["next"] == null) {
                            break;
                        }

                        page++;

                    } catch (Exception e) {
                        Console.WriteLine($"\nError on page {page}: {e.Message}");
                        break;
                    }
                }

                Console.WriteLine();

                // Display and save results
                _display_results(status_count, total_scanned);
                var report_path = _save_report(status_count, total_scanned);

                return (status_count, report_path);
            }
        }

        private void _display_results(Dictionary<string, List<Dictionary<string, object>>> status_count, int total_scanned) {
            Console.WriteLine("\n" + new string('=', 60));
            Console.WriteLine("Scan Results:");
            Console.WriteLine(new string('=', 60));
            Console.WriteLine($"Total scanned: {total_scanned:N0} files");
            Console.WriteLine($"- Initial status: {status_count["initial"].Count:N0}");
            Console.WriteLine($"- Processing: {status_count["processing"].Count:N0}");
            Console.WriteLine($"- Done: {status_count["done"].Count:N0}");
            Console.WriteLine($"- Failed: {status_count["failed"].Count:N0}");
            Console.WriteLine($"- Other: {status_count["other"].Count:N0}");

            // Show problematic files
            var problematic = new List<Dictionary<string, object>>();
            problematic.AddRange(status_count["initial"]);
            problematic.AddRange(status_count["processing"]);
            problematic.AddRange(status_count["failed"]);

            if (problematic.Count > 0) {
                Console.WriteLine($"\n📋 Files with issues ({problematic.Count} total):");
                Console.WriteLine(new string('-', 40));
                for (int i = 0; i < Math.Min(10, problematic.Count); i++) {
                    var file = problematic[i];
                    var created_time = _format_timestamp(file["created_at"]);
                    Console.WriteLine($"• {file["filename"]} ({file["status"]}) - {created_time}");
                }

                if (problematic.Count > 10) {
                    Console.WriteLine($"... and {problematic.Count - 10} more files");
                }
            } else {
                Console.WriteLine("\n✅ All scanned files are in 'done' status!");
            }
        }

        private string _format_timestamp(object timestamp) {
            if (timestamp == null) return "Unknown";
            try {
                var tsStr = timestamp.ToString();
                if (long.TryParse(tsStr, out long tsLong)) {
                    return DateTimeOffset.FromUnixTimeMilliseconds(tsLong).ToString("yyyy-MM-dd HH:mm:ss");
                }
                return tsStr;
            } catch {
                return timestamp.ToString();
            }
        }

        private string _save_report(Dictionary<string, List<Dictionary<string, object>>> status_count, int total_scanned) {
            var report = new Dictionary<string, object> {
                {"scan_time", DateTime.Now.ToString("o")},
                {"knowledge_base_id", knowledge_base_id},
                {"total_scanned", total_scanned},
                {"summary", new Dictionary<string, int> {
                    {"initial", status_count["initial"].Count},
                    {"processing", status_count["processing"].Count},
                    {"done", status_count["done"].Count},
                    {"failed", status_count["failed"].Count},
                    {"other", status_count["other"].Count}
                }},
                {"initial_files", status_count["initial"]},
                {"processing_files", status_count["processing"]},
                {"failed_files", status_count["failed"]},
                {"other_files", status_count["other"]}
            };

            var report_path = $"status_scan_{DateTime.Now:yyyyMMdd_HHmmss}.json";
            var jsonString = JsonSerializer.Serialize(report, new JsonSerializerOptions { WriteIndented = true });
            File.WriteAllText(report_path, jsonString);

            Console.WriteLine($"\n📄 Detailed report saved to: {report_path}");
            return report_path;
        }
    }

    public static void main() {
        // Scan knowledge base file statuses
        //
        // This script will scan all files (or a limited number of pages) in your knowledge base
        // and report the distribution of file statuses. It's useful for identifying files that
        // are stuck in 'initial', 'processing', or 'failed' states.
        //
        // Usage:
        // 1. Set your API_KEY and KNOWLEDGE_BASE_ID at the top of this file
        // 2. Run the program
        //
        // Optional: Modify max_pages parameter to limit scanning to first N pages

        Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
        Debug.Assert(KNOWLEDGE_BASE_ID != "<your-knowledge-base-id>", "Please set your knowledge base id");

        var scanner = new KnowledgeBaseStatusScanner(API_KEY, KNOWLEDGE_BASE_ID);

        // Scan all pages (set max_pages=50 to limit to first 50 pages)
        var (status_count, report_path) = scanner.scan_files_by_status(max_pages: null);

        // Print summary
        int problematic_count = status_count["initial"].Count + status_count["processing"].Count + status_count["failed"].Count;
        if (problematic_count > 0) {
            Console.WriteLine($"\n⚠️  Found {problematic_count} files that may need attention.");
            Console.WriteLine($"   Check the detailed report: {report_path}");
        } else {
            Console.WriteLine($"\n✅ Knowledge base looks healthy!");
        }
    }
}
