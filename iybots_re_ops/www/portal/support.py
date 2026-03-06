import frappe
from iybots_re_ops.iybots_real_estate_ops.portal_utils import require_client_or_redirect

no_cache = 1
base_template_path = "iybots_re_ops/templates/portal_base.html"


def get_context(context):
	client = require_client_or_redirect()
	context.client = client
	context.active_page = "support"
	context.title = "Support"
	context.whatsapp_number = "2348000000000"  # Update with real number
	context.support_email = "support@iybots.com"
