openerp.marcos_ipf = function (instance, local) {
    var _t = openerp.web._t,
        _lt = openerp.web._lt;
    var QWeb = openerp.web.qweb;

    local.IpfPrint = instance.web.form.FormWidget.extend({
        events: {
            "click #ipf_print_button": "ipf_print"
        },
        start: function () {
            var self = this;
            this.invoice_id = 0;
            this.nif = 0;
            this.$el.append("<button id='ipf_print_button' class='oe_inline oe_stat_button' icon='fa-print'><div class='stat_button_icon fa fa-print fa-fw'></div><div>Imprimir fiscal</div></button>");
        },
        ipf_print: function () {
            var self = this;
            var active_model = self.field_manager.model;
            var active_id = self.field_manager.datarecord.id || self.field_manager.dataset.context.id;
            //var invoice_number = this.field_manager.get_field_value("number");
            return new openerp.web.Model("ipf.printer.config").call("ipf_print", [], {
                context: new instance.web.CompoundContext({
                    active_model: active_model,
                    active_id: active_id
                })
            })
                .then(function (data) {
                    return self.print_receipt(data)
                });
        },
        print_done: function () {
            var self = this;
            return new openerp.web.Model("ipf.printer.config").call("print_done", [[self.invoice_id, self.nif]], {context: new instance.web.CompoundContext()})
                .then(function (response) {
                    console.log("print_done");
                    console.log(response);
                    return response;
                })
        },
        print_receipt: function (data) {
            var self = this;
            this.invoice_id = data.invoice_id;
            console.log(data);
            //self.makeCorsRequest(data);
            $.ajax({
                type: 'POST',
                url: data.host + "/invoice",
                data: JSON.stringify(data)
            })
                .done(function (response) {
                    console.log("done");
                    console.log(response);
                    var message = JSON.parse(response);
                    self.nif = message.response.nif;
                    self.print_done();
                })
                .fail(function (response) {
                    console.log(response);
                    console.log("fail");
                    return alert("La impresora require mantenimiento!.");

                });
        },
        createCORSRequest: function (method, url) {
            var self = this;
            var xhr = new XMLHttpRequest();
            if ("withCredentials" in xhr) {
                // XHR for Chrome/Firefox/Opera/Safari.
                xhr.open(method, url, true);
            } else if (typeof XDomainRequest != "undefined") {
                // XDomainRequest for IE.
                xhr = new XDomainRequest();
                xhr.open(method, url);
            } else {
                // CORS not supported.
                xhr = null;
            }
            return xhr;
        },
        getTitle: function (text) {
            var self = this;
            return text.match('<title>(.*)?</title>')[1];
        }
    });


    openerp.web.form.custom_widgets.add("ipf_js_print_button", "instance.marcos_ipf.IpfPrint")
}