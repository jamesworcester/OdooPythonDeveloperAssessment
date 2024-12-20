/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { Thread } from "@mail/core/common/thread_model";
import { rpc } from '@web/core/network/rpc';

patch(Thread.prototype,  {
    async post() {
        const message = await super.post(...arguments)

        if (message.id) {
            const result = await rpc({
                route: '/web/dataset/call_kw/mail.message/write',
                params: {
                    model: 'mail.message',
                    method: 'write',
                    args: [[message.id], {
                        'vendor_bill_admin_only': 1
                    }]
                }
            })
        }
        return message
    }
});
