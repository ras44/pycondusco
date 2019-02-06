#    Copyright (C) 2018 Roland Stevenson
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#==============================================================================
import unittest
from google.cloud import bigquery

class TestGBQConn(unittest.TestCase):

    def test_gbq_conn(self):
        client = bigquery.Client()
        query_job = client.query("""
            SELECT
              CONCAT(
                'https://stackoverflow.com/questions/',
                CAST(id as STRING)) as url,
              view_count
            FROM `bigquery-public-data.stackoverflow.posts_questions`
            WHERE tags like '%google-bigquery%'
            ORDER BY view_count DESC
            LIMIT 10""")

        results = query_job.result()  # Waits for job to complete.

        for row in results:
            print("{} : {} views".format(row.url, row.view_count))

if __name__ == '__main__':
    unittest.main()

