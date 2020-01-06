odoo.define('solixyProject.kanban_view', function (require) {
    "use strict";
    var form_widget = require('web.form_widgets');
    var core = require('web.core');
    var _t = core._t;
    form_widget.WidgetButton.include({
        on_click: function () {
            if (this.node.attrs.custom === "click") {
                this.do_warn(_t("Form"), _t("The record could not be found in the database."), true);
            }
            this._super();
        },
    });
});