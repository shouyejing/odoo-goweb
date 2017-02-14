openerp.web_multi_uploader = function(session) {
    var mail = session.mail;
    session.mail.ThreadComposeMessage.include({
        on_attachment_change: function (event) {
            event.stopPropagation();
            var self = this;
            var $target = $(event.target);
            if ($target.val() !== '') {
                var filename = $target.val().replace(/.*[\\\/]/,'');

                // if the files exits for this answer, delete the file before upload
                var attachments=[];
                for (var i in this.attachment_ids) {
                    if ((this.attachment_ids[i].filename || this.attachment_ids[i].name) == filename) {
                        if (this.attachment_ids[i].upload) {
                            return false;
                        }
                        this.ds_attachment.unlink([this.attachment_ids[i].id]);
                    } else {
                        attachments.push(this.attachment_ids[i]);
                    }
                }
                this.attachment_ids = attachments;

                // submit file
                this.$('form.oe_form_binary_form').submit();

                this.$(".oe_attachment_file").hide();

                var target = $target.get(0);
                _.each(target.files, function(file){
                    self.attachment_ids.push({
                        'id': 0,
                        'name': file.name,
                        'filename': file.name,
                        'url': '',
                        'upload': true
                    });
                });
                this.display_attachments();
            }
        },
        on_attachment_loaded: function (event, result) {
            if (result.erorr) {
                this.do_warn( session.web.qweb.render('mail.error_upload'), result.error);
                this.attachment_ids = _.filter(this.attachment_ids, function (val) { return !val.upload; });
            } else {
                for (var i in this.attachment_ids) {
                    if (_.contains(_.values(result), this.attachment_ids[i].filename) && this.attachment_ids[i].upload) {
                        var filename = this.attachment_ids[i].filename;
                        var id = _.invert(result)[filename];
                        this.attachment_ids[i]={
                            'id': id,
                            'name': filename,
                            'filename': filename,
                            'url': mail.ChatterUtils.get_attachment_url(this.session, this.id, id)
                        };
                    }
                }
            }
            this.display_attachments();
            var $input = this.$('input.oe_form_binary_file');
            $input.after($input.clone(true)).remove();
            this.$(".oe_attachment_file").show();
        },

    });
};