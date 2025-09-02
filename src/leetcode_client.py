import time
import requests
import json


class LeetcodeClient:
    LOGIN_PATH = 'accounts/login/'
    GRAPHQL_PATH = 'graphql/'

    def __init__(
            self,
            LEETCODE_SESSION,
            CSRF_TOKEN,
            sleep_time=5,
            base_url='https://leetcode.cn/',
            logger=None) -> None:
        self.sleep_time = sleep_time
        self.endpoint = base_url
        self.logger = logger

        self.client = requests.session()

        # 设置 cookies
        self.client.cookies.set('LEETCODE_SESSION', LEETCODE_SESSION)
        self.client.cookies.set('csrftoken', CSRF_TOKEN)

        self.client.encoding = "utf-8"

        self.headers = {
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'X-CSRFToken': CSRF_TOKEN,  
            'Referer': base_url
        }

    def login(self) -> None:
        """验证硬编码的 cookies 是否有效"""
        ATTEMPT = 3

        for try_cnt in range(ATTEMPT):
            try:
                test_url = self.endpoint + "api/submissions/?offset=0&limit=1"

                self.logger.info(f"Testing authentication with: {test_url}")
                result = self.client.get(test_url, headers=self.headers)

                self.logger.info(f"Auth test response status: {result.status_code}")

                if result.ok:
                    try:
                        data = result.json()
                        self.logger.info("Authentication successful - cookies are valid!")
                        self.logger.info(f"Response has submissions_dump: {'submissions_dump' in data}")
                        return
                    except json.JSONDecodeError:
                        self.logger.error(f"Failed to parse response: {result.text[:500]}")
                else:
                    self.logger.warning(f"Request failed with status: {result.status_code}")
                    self.logger.warning(f"Response: {result.text[:500]}")

                    if result.status_code == 403:
                        self.logger.error("403 Forbidden - CSRF token may be invalid")
                        self.logger.error("Please get a fresh CSRF token from browser")
                    elif result.status_code == 401:
                        self.logger.error("401 Unauthorized - Session cookie may be expired")
                        self.logger.error("Please get a fresh LEETCODE_SESSION from browser")

            except Exception as e:
                self.logger.error(f"Login verification failed with error: {e}")
                import traceback
                self.logger.error(traceback.format_exc())

            if try_cnt != ATTEMPT - 1:
                self.logger.info(f"Retrying in {self.sleep_time} seconds...")
                time.sleep(self.sleep_time)

        self.logger.error("All login attempts failed!")
        raise Exception("LoginError: Cookie validation failed! Please update your LEETCODE_SESSION and CSRF token.")

    def downloadCode(self, submission) -> str:
        with open('query/query_download_submission', 'r') as f:
            query_string = f.read()

        data = {
            'query': query_string,
            'operationName': "mySubmissionDetail",
            "variables": {
                "id": submission["id"]
            }
        }

        response = self.client.post(
            self.endpoint +
            self.GRAPHQL_PATH,
            json=data,
            headers=self.headers)
        submission_details = response.json()["data"]["submissionDetail"]
        return submission_details

    def getSubmissionList(self, page_num):
        limit = 5
        offset = page_num * limit

        self.logger.info(
            f'Now scraping submissions list for page:{page_num} (offset={offset}, limit={limit})'
        )

        submissions_url = f"{self.endpoint}api/submissions/?offset={offset}&limit={limit}"

        max_retries = 3
        for retry in range(max_retries):
            try:
                response = self.client.get(submissions_url, headers=self.headers)

                if not response.ok:
                    self.logger.warning(f"Request failed with status {response.status_code}")
                    self.logger.warning(f"Response: {response.text[:500]}")

                    if response.status_code == 429:
                        wait_time = (retry + 1) * self.sleep_time
                        self.logger.info(f"Rate limited, waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue

                result = response.json()

                if "detail" in result:
                    error_detail = result.get("detail", "Unknown error")
                    self.logger.error(f"API error: {error_detail}")

                    return {"submissions_dump": [], "has_next": False}


                if "submissions_dump" not in result:
                    self.logger.error(f"Unexpected response structure: {list(result.keys())}")
                    self.logger.debug(f"Full response: {json.dumps(result, ensure_ascii=False)[:500]}")
                    return {"submissions_dump": [], "has_next": False}


                submission_count = len(result.get("submissions_dump", []))
                self.logger.info(f"Successfully fetched {submission_count} submissions")

                return result

            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON response: {e}")
                self.logger.error(f"Response text: {response.text[:500]}")

                if retry < max_retries - 1:
                    time.sleep(self.sleep_time)
                    continue

            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                import traceback
                self.logger.error(traceback.format_exc())

                if retry < max_retries - 1:
                    time.sleep(self.sleep_time)
                    continue

        self.logger.error("All attempts to fetch submissions failed")
        return {"submissions_dump": [], "has_next": False}
