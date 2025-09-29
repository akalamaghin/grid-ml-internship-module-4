import os
import shutil
import unittest
import requests


API_URL = "http://localhost:8000"
UPLOAD_DIR = "./test_uploads"
DOWNLOAD_DIR = "./test_downloads"


class TestFileHostingAPI(unittest.TestCase):

    def setUp(self):
        """Ensure download directory exists before each test."""
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    def tearDown(self):
        """Remove download directory after each test."""
        if os.path.exists(DOWNLOAD_DIR):
            shutil.rmtree(DOWNLOAD_DIR)
            print(f"[v] Cleaned up {DOWNLOAD_DIR}")

    def test_file_upload_list_download(self):

        # Step 1: Upload all files from UPLOAD_DIR
        for filename in os.listdir(UPLOAD_DIR):
            filepath = os.path.join(UPLOAD_DIR, filename)
            with open(filepath, "rb") as fp:
                content = fp.read()

            response = requests.post(f"{API_URL}/files/{filename}", data=content)
            self.assertEqual(
                response.status_code, 200,
                f"[x] Upload failed for {filename}: {response.status_code} {response.text}"
            )
            print(f"[v] Uploaded {filename} to the server")

        # Step 2: Get file list from API
        response = requests.get(f"{API_URL}/files")
        self.assertEqual(response.status_code, 200, "[x] Failed to fetch file list")
        file_list = response.json()
        self.assertIsInstance(file_list, list, "[x] File list is not a JSON array")
        print(f"[v] Retrieved file list form the server: {file_list}")

        # Step 3: Download each file in the list
        for filename in file_list:
            response = requests.get(f"{API_URL}/files/{filename}")
            self.assertEqual(
                response.status_code, 200,
                f"[x] Failed to download {filename}: {response.status_code} {response.text}"
            )

            file_path = os.path.join(DOWNLOAD_DIR, filename)
            with open(file_path, "wb") as f:
                f.write(response.content)

            self.assertTrue(
                os.path.exists(file_path), f"[x] Downloaded file {filename} not found on disk"
            )
            print(f"[v] Downloaded {filename} from the server to {file_path} and verified")

        # Step 4: Delete each uploaded file
        for filename in file_list:
            response = requests.delete(f"{API_URL}/files/{filename}")
            self.assertEqual(
                response.status_code, 200,
                f"[x] Failed to delete {filename}: {response.status_code} {response.text}"
            )
            print(f"[v] Deleted {filename} from the server")

        # Step 5: Verify file list is empty again
        response = requests.get(f"{API_URL}/files")
        self.assertEqual(response.status_code, 200, "[x] Failed to fetch file list after deletions")
        file_list_after = response.json()
        self.assertEqual(len(file_list_after), 0, f"[x] File list not empty after deletions: {file_list_after}")
        print(f"[v] Verified server's file list is empty after the deletions: {file_list_after}")


if __name__ == "__main__":
    unittest.main()
