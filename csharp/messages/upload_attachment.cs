
using mimetypes;

using Path = pathlib.Path;

using requests;

using os;

using Utils;



using System.Collections.Generic;

using System;

public static class upload_attachment {
    
    public static string TEST_IMAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(@__file__))), "test_files", "異型介紹.txt");
    
    public static object main(object file_path) {
        file_path = Path(file_path);
        var headers = new Dictionary<object, object> {
            {
                "Authorization",
                $"Api-Key {Config.API_KEY}"}};
        (mime_type, _) = mimetypes.guess_type(file_path);
        using (var file = open(file_path, "rb")) {
            files = new Dictionary<object, object> {
                {
                    "file",
                    (file_path.name, file, mime_type)}};
            response = requests.post($"{Config.BASE_URL}attachments/", headers: headers, files: files);
        }
        Console.WriteLine(response.json());
    }
    
    static upload_attachment() {
        main(TEST_IMAGE_PATH);
    }
    
    static upload_attachment() {
        if (@__name__ == "__main__") {
        }
    }
}
