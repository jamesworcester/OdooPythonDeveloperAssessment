/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Composer } from "@mail/core/common/composer";

patch(Composer.prototype,  {
    onChange(ev) {
        this.thread.vendor_bill_admin_only = ev.target.checked;
    },

    get postData() {
        const postData = super.postData;

        return {
            ...postData,
            vendor_bill_admin_only: this.props.vendor_bill_admin_only,
        };
    }
});