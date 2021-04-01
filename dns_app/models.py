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


from django.db import models


class UniqueMsisdn(models.Model):
    id = models.BigAutoField(primary_key=True)
    msisdn = models.CharField(max_length=50)
    msisdn_received = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return "<UniqueMsisdn {}, {}, {}>".format(self.id, self.msisdn, self.msisdn_received)


class UniqueEmail(models.Model):
    id = models.BigAutoField(primary_key=True)
    email = models.CharField(max_length=50)
    email_received = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return "<UniqueEmail {}, {}, {}>".format(self.id, self.email, self.email_received)


class Sms(models.Model):
    id = models.BigAutoField(primary_key=True)
    sms_to = models.CharField(max_length=50)
    sms_from = models.CharField(max_length=50)
    imei = models.CharField(max_length=50, null=True, blank=True)
    # subsystem = models.ForeignKey(SubSystems, on_delete=models.SET_NULL, null=True, blank=True)
    subsystem = models.CharField(max_length=100)
    filename = models.CharField(max_length=200, null=True, blank=True)
    sms_delivered = models.DateTimeField(auto_now_add=True, null=True)
    operator = models.CharField(max_length=100)
    campaign_id = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return "<SMS {}, {}, {}, {}, {}>".format(self.id, self.sms_to, self.imei, self.subsystem, self.operator)


class SmsContent(models.Model):
    id = models.BigAutoField(primary_key=True)
    sms_content = models.TextField()
    sms = models.ForeignKey(Sms, on_delete=models.CASCADE, related_name="sms_contents")

    def __str__(self):
        return "sms-id: {}, sms-content: {}".format(self.id, self.sms_content)


class Email(models.Model):
    id = models.BigAutoField(primary_key=True)
    email_to = models.EmailField(max_length=500)
    email_from = models.EmailField(max_length=500)
    imei = models.CharField(max_length=50, null=True, blank=True)
    subsystem = models.CharField(max_length=100)
    filename = models.CharField(max_length=200, null=True, blank=True)
    email_delivered = models.DateTimeField(auto_now_add=True, null=True)
    campaign_id = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return "<Email {}, {}, {}, {}>".format(self.id, self.email_to, self.email_from, self.subsystem)


class EmailContent(models.Model):
    id = models.BigAutoField(primary_key=True)
    email_subject = models.TextField()
    email_content = models.TextField()
    email = models.ForeignKey(Email, on_delete=models.CASCADE)

    def __str__(self):
        return "<EmailContent {}, {}, {}>".format(self.id, self.email_subject, self.email_content)
