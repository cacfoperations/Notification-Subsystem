"""
Copyright (c) 2018-2021 Qualcomm Technologies, Inc.

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted (subject to the
limitations in the disclaimer below) provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.
* Neither the name of Qualcomm Technologies, Inc. nor the names of its contributors may be used to endorse or promote
products derived from this software without specific prior written permission.
* The origin of this software must not be misrepresented; you must not claim that you wrote the original software.
If you use this software in a product, an acknowledgment is required by displaying the trademark/log as per the details
provided here: https://www.qualcomm.com/documents/dirbs-logo-and-brand-guidelines
* Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
* This notice may not be removed or altered from any source distribution.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY THIS LICENSE. THIS SOFTWARE IS PROVIDED BY
THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
 BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 POSSIBILITY OF SUCH DAMAGE.
"""


from django.core.management.base import BaseCommand
from ...models import UniqueMsisdn
from django.db import connection


# noinspection SqlNoDataSourceInspection
class Command(BaseCommand):
    help = 'update Unique-MSISDN model'

    # def add_arguments(self, parser):
    #     parser.add_argument('date_from', type=str, help="Date in YYYY-MM-DD from which you want to update DB")

    def handle(self, *args, **options):
        # date_from = options['date_from']

        with connection.cursor() as cursor:

            print("Processing.......")

            # for q in Sms.objects.raw('SELECT id, sms_to FROM dns_app_sms WHERE sms_to NOT IN (SELECT msisdn FROM dns_app_uniquemsisdn);'):
            cursor.execute("""SELECT sms_to 
                              FROM   dns_app_sms t1
                              EXCEPT   -- "ALL" keeps duplicates and makes it faster
                              SELECT msisdn
                              FROM   dns_app_uniquemsisdn t2;""")
            rows = cursor.fetchall()

            for row in rows:
                um_obj = UniqueMsisdn(msisdn=row[0])
                um_obj.save()
                print("inserting {} in unique_msisdn model".format(row[0]))

            print("\n Total records updated: ", len(rows))