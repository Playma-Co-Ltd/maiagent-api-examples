
using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;
using System.Threading;
using System.Diagnostics;
using Utils;

public static class delete_duplicate_files {

    // Configuration - Replace with your actual values
    public static string API_KEY = "<your-api-key>";
    public static string KNOWLEDGE_BASE_ID = "<your-knowledge-base-id>";   // 你的知識庫 ID

    // Path to your integrity check report - Replace with your actual path
    public static string INTEGRITY_REPORT_PATH = "<path-to-your-integrity-check-report>";  // e.g., 'upload_outputs/json_files_4e9ffa82/reports/....json'

    public static List<Dictionary<string, object>> load_duplicate_files(string file_path) {
        // Load duplicate files from an integrity check report
        //
        // Args:
        //     file_path: Path to the integrity check JSON file
        //
        // Returns:
        //     List of duplicate files to delete

        if (!File.Exists(file_path)) {
            Console.WriteLine($"❌ File not found: {file_path}");
            Console.WriteLine("Please check the file path and make sure the integrity check report exists.");
            return new List<Dictionary<string, object>>();
        }

        try {
            var jsonString = File.ReadAllText(file_path);
            var data = JsonSerializer.Deserialize<Dictionary<string, object>>(jsonString);

            // Look for extra_files (files in KB but not in upload records)
            if (data.ContainsKey("extra_files")) {
                var extra_files = JsonSerializer.Deserialize<List<Dictionary<string, object>>>(data["extra_files"].ToString());
                if (extra_files.Count > 0) {
                    Console.WriteLine($"📋 Found {extra_files.Count} duplicate/extra files in integrity report");
                    return extra_files;
                } else {
                    Console.WriteLine("✅ No duplicate files found in the report");
                    return new List<Dictionary<string, object>>();
                }
            } else {
                Console.WriteLine("✅ No duplicate files found in the report");
                return new List<Dictionary<string, object>>();
            }

        } catch (Exception e) {
            Console.WriteLine($"❌ Error reading file: {e.Message}");
            return new List<Dictionary<string, object>>();
        }
    }

    public static (List<Dictionary<string, object>>, List<Dictionary<string, object>>) delete_duplicate_files_action(List<Dictionary<string, object>> duplicate_files) {
        // Delete duplicate files from knowledge base
        //
        // Args:
        //     duplicate_files: List of file info dicts with 'knowledge_file_id' and 'filename'

        if (duplicate_files.Count == 0) {
            Console.WriteLine("❌ No files to delete");
            return (new List<Dictionary<string, object>>(), new List<Dictionary<string, object>>());
        }

        var maiagent_helper = new MaiAgentHelper(API_KEY);

        Console.WriteLine(new string('=', 60));
        Console.WriteLine("Files to be deleted:");
        Console.WriteLine(new string('=', 60));

        // Show files to be deleted
        for (int i = 0; i < Math.Min(10, duplicate_files.Count); i++) {
            var file = duplicate_files[i];
            var filename = file.ContainsKey("filename") ? file["filename"].ToString() : "Unknown";
            var file_id = file.ContainsKey("knowledge_file_id") ? file["knowledge_file_id"].ToString() : "Unknown";
            var created_at = file.ContainsKey("created_at") ? file["created_at"].ToString() : "Unknown";
            Console.WriteLine($"{i + 1}. {filename}");
            Console.WriteLine($"   ID: {file_id}");
            Console.WriteLine($"   Created: {created_at}");
            Console.WriteLine();
        }

        if (duplicate_files.Count > 10) {
            Console.WriteLine($"... and {duplicate_files.Count - 10} more files");
        }

        Console.WriteLine(new string('=', 60));
        Console.Write("⚠️  Are you sure you want to delete these duplicate files? Type 'YES' to confirm: ");
        var confirm = Console.ReadLine();
        if (confirm != "YES") {
            Console.WriteLine("❌ Operation cancelled");
            return (new List<Dictionary<string, object>>(), new List<Dictionary<string, object>>());
        }

        // Perform deletion
        Console.WriteLine("\n🗑️  Starting deletion process...");
        Console.WriteLine(new string('-', 40));

        var deleted_files = new List<Dictionary<string, object>>();
        var failed_deletions = new List<Dictionary<string, object>>();

        for (int i = 0; i < duplicate_files.Count; i++) {
            try {
                var file = duplicate_files[i];
                var file_id = file["knowledge_file_id"].ToString();
                var filename = file["filename"].ToString();

                // Delete file
                maiagent_helper.delete_knowledge_file(KNOWLEDGE_BASE_ID, file_id);
                deleted_files.Add(file);
                Console.WriteLine($"✓ Deleted: {filename}");

                // Progress indicator
                if ((i + 1) % 10 == 0) {
                    Console.WriteLine($"   Progress: {i + 1}/{duplicate_files.Count}");
                }

                // Rate limiting to avoid overwhelming the API
                Thread.Sleep(500);

            } catch (Exception e) {
                var file = duplicate_files[i];
                var filename = file["filename"].ToString();

                // Note: API might return 500 error even when deletion succeeds
                if (e.Message.Contains("500") || e.Message.Contains("Internal Server Error")) {
                    // Assume deletion was successful despite 500 error
                    deleted_files.Add(file);
                    Console.WriteLine($"✓ Deleted: {filename} (API returned 500 but likely successful)");
                } else if (e.Message.Contains("409") || e.Message.Contains("Conflict")) {
                    Console.WriteLine($"⚠️  Skipped: {filename} (file is being processed, cannot delete)");
                    failed_deletions.Add(new Dictionary<string, object> {
                        {"file", file},
                        {"error", "File is being processed"}
                    });
                } else {
                    failed_deletions.Add(new Dictionary<string, object> {
                        {"file", file},
                        {"error", e.Message}
                    });
                    Console.WriteLine($"❌ Failed: {filename} - {e.Message}");
                }
            }
        }

        // Save deletion log
        var deletion_log = new Dictionary<string, object> {
            {"timestamp", DateTime.Now.ToString("o")},
            {"knowledge_base_id", KNOWLEDGE_BASE_ID},
            {"integrity_report_used", INTEGRITY_REPORT_PATH},
            {"total_files", duplicate_files.Count},
            {"successful_deletions", deleted_files.Count},
            {"failed_deletions_count", failed_deletions.Count},
            {"deleted_files", deleted_files},
            {"failed_deletions", failed_deletions}
        };

        var log_filename = $"duplicate_deletion_log_{DateTime.Now:yyyyMMdd_HHmmss}.json";
        var jsonString = JsonSerializer.Serialize(deletion_log, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(log_filename, jsonString);

        // Summary
        Console.WriteLine("\n" + new string('=', 60));
        Console.WriteLine("Deletion Summary:");
        Console.WriteLine(new string('=', 60));
        Console.WriteLine($"✅ Successfully deleted: {deleted_files.Count} files");
        Console.WriteLine($"❌ Failed deletions: {failed_deletions.Count} files");
        Console.WriteLine($"📄 Deletion log saved to: {log_filename}");

        if (failed_deletions.Count > 0) {
            Console.WriteLine($"\nFiles that couldn't be deleted:");
            foreach (var failed in failed_deletions) {
                var failedFile = (Dictionary<string, object>)failed["file"];
                Console.WriteLine($"  - {failedFile["filename"]}: {failed["error"]}");
            }
        }

        return (deleted_files, failed_deletions);
    }

    public static void main() {
        // Delete duplicate files from knowledge base
        //
        // This script is designed to clean up duplicate files found after upload completion.
        // It reads an integrity check report and deletes the extra files identified.
        //
        // Usage:
        // 1. Set your API_KEY and KNOWLEDGE_BASE_ID at the top of this file
        // 2. Set INTEGRITY_REPORT_PATH to point to your integrity check report
        //    Example: 'batch_upload/upload_outputs/json_files_4e9ffa82/reports/integrity_check_20250801_102645.json'
        // 3. Run the program
        //
        // The script will:
        // - Read the integrity check report from the specified path
        // - Show you which duplicate files will be deleted
        // - Ask for confirmation before deletion
        // - Save a detailed log of the deletion process
        //
        // Note: The integrity check report should contain 'extra_files' - these are files
        // that exist in the knowledge base but were not part of your original upload batch.

        Debug.Assert(API_KEY != "<your-api-key>", "Please set your API key");
        Debug.Assert(KNOWLEDGE_BASE_ID != "<your-knowledge-base-id>", "Please set your knowledge base id");
        Debug.Assert(INTEGRITY_REPORT_PATH != "<path-to-your-integrity-check-report>", "Please set the path to your integrity check report");

        Console.WriteLine("Knowledge Base Duplicate File Cleaner");
        Console.WriteLine("====================================");
        Console.WriteLine($"Using integrity report: {INTEGRITY_REPORT_PATH}");
        Console.WriteLine();

        // Load and delete duplicate files
        var duplicate_files = load_duplicate_files(INTEGRITY_REPORT_PATH);
        if (duplicate_files.Count > 0) {
            delete_duplicate_files_action(duplicate_files);
        } else {
            Console.WriteLine("✅ No duplicate files to delete!");
        }
    }
}
