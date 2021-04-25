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


from rest_framework import serializers
from .models import Sms, SmsContent, Email, EmailContent, UniqueMsisdn, UniqueEmail
from dns_app.common.validators import CustomValidations as cv


class SmsContentSerializer(serializers.ModelSerializer):

    class Meta:
        model = SmsContent
        fields = ['id', 'sms_content', 'sms']


class SmsSerializer(serializers.ModelSerializer):

    sms_to = serializers.CharField(validators=[cv.chk_msisdn])
    sms_from = serializers.CharField(validators=[cv.chk_shortcode])
    operator = serializers.CharField(required=False, validators=[cv.chk_operators])
    subsystem = serializers.CharField(validators=[cv.chk_subsystems])
    imei = serializers.CharField(required=False, validators=[cv.check_imei])

    class Meta:
        model = Sms
        fields = ['id', 'sms_to', 'sms_from', 'imei', 'subsystem', 'filename', 'sms_delivered', 'operator']

    #Field Level Validation
    # def validate_sms_to(self, value):
    #     if len(value) < 11 or len(value) > 12:
    #         raise serializers.ValidationError('MSISDN format is not correct')
    #     return value

    # object Level Validation
    # def validate(self, data):
    #     print(data)
    #     imei = data.get('imei')
    #     fn = data.get('filename')
    #     print(imei, fn)
    #     # if len(imei) < 14 or len(imei) > 16:
    #     #     raise serializers.ValidationError('IMEI is not correct')
    #     if fn != "ABC":
    #         raise serializers.ValidationError('File name is not correct')
    #     return data


class EmailSerializer(serializers.ModelSerializer):

    email_to = serializers.CharField(validators=[cv.chk_email_id])
    email_from = serializers.CharField(validators=[cv.chk_email_id])
    imei = serializers.CharField(required=False, validators=[cv.check_imei])
    subsystem = serializers.CharField(validators=[cv.chk_subsystems])

    class Meta:
        model = Email
        fields = "__all__"


class EmailContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailContent
        fields = "__all__"


class UniqueMsisdnSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniqueMsisdn
        fields = "__all__"


class UniqueEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UniqueEmail
        fields = "__all__"
