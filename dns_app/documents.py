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


from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import UniqueMsisdn, UniqueEmail, Sms, SmsContent, Email, EmailContent


@registry.register_document
class UniqueMsisdnDocument(Document):

    class Index:
        name = 'dns_unique_msisdn'
        settings = {'number_of_shards': 5,
                    'number_of_replicas': 0}

    class Django:
        model = UniqueMsisdn
        fields = [
            'msisdn',
            'msisdn_received'
        ]


@registry.register_document
class UniqueEmailDocument(Document):

    class Index:
        name = 'dns_unique_email'
        settings = {'number_of_shards': 5,
                    'number_of_replicas': 0}

    class Django:
        model = UniqueEmail
        fields = [
            'email',
            'email_received'
        ]


@registry.register_document
class SmsDocument(Document):

    class Index:
        name = 'dns_sms'
        settings = {'number_of_shards': 5,
                    'number_of_replicas': 0}

    class Django:
        model = Sms
        fields = [
            'sms_to',
            'sms_from',
            'imei',
            'subsystem',
            'filename',
            'sms_delivered',
            'operator',
            'campaign_id',
        ]


@registry.register_document
class SmsContentDocument(Document):

    sms = fields.ObjectField(properties={
        'sms_to': fields.TextField(),
        'sms_from': fields.TextField(),
        'imei': fields.TextField(),
        'filename': fields.TextField(),
        'operator': fields.TextField(),
        'subsystem': fields.TextField(),
        'sms_delivered': fields.DateField(),
        'campaign_id': fields.TextField(),
        'pk': fields.IntegerField(),
    })

    class Index:
        name = 'dns_sms_content'
        settings = {'number_of_shards': 5,
                    'number_of_replicas': 0}

    class Django:
        model = SmsContent
        fields = [
            'sms_content',
        ]


@registry.register_document
class EmailDocument(Document):

    class Index:
        name = 'dns_email'
        settings = {'number_of_shards': 5,
                    'number_of_replicas': 0}

    class Django:
        model = Email
        fields = [
            'email_to',
            'email_from',
            'imei',
            'subsystem',
            'filename',
            'email_delivered',
            'campaign_id',
        ]


@registry.register_document
class EmailContentDocument(Document):

    email = fields.ObjectField(properties={
        'email_to': fields.TextField(),
        'email_from': fields.TextField(),
        'imei': fields.TextField(),
        'filename': fields.TextField(),
        'subsystem': fields.TextField(),
        'email_delivered': fields.DateField(),
        'campaign_id': fields.TextField(),
        'pk': fields.IntegerField(),
    })

    class Index:
        name = 'dns_email_content'
        settings = {'number_of_shards': 5,
                    'number_of_replicas': 0}

    class Django:
        model = EmailContent
        fields = [
            'email_subject',
            'email_content',
        ]
