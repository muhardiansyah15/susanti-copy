odoo.define('susanti_vendor_portal.upload_attachment', function(require) {
    "use strict";
    var PublicWidget = require('web.public.widget');
    var ajax = require('web.ajax');
    var Template = PublicWidget.Widget.extend({
        selector: '.upload_attachment',
        events: {
            'click #btnShowModal': '_onClickShowModal',
            'click .close_modal': '_onClickCloseModal',
            'change #attachment_proof': '_onChangeAttachmentProof',
            'click #attachment_proof_update': '_onClickUpdateAttachment',
            'click #vendorScreenBtnShowAttachment': '_onClickShowAttachment',
            'click #refresh_vendor_attachment': '_onClickShowAttachment',
        },

        _onClickShowModal: function(event) {
            event.preventDefault();
            this.$el.find('#myAttachmentModal').css("display", "block")
        },

        _onClickCloseModal: function() {
            this.$el.find('#myAttachmentModal').css("display", "none")
        },

        _onChangeAttachmentProof: function(ev) {
            const files = ev.target.files;
            var fileList = [];
            for (let i = 0; i < files.length; i++) {
                var reader = new FileReader();
                var reader_content = reader.readAsDataURL(files[i]);
                reader.onload = function(reader_content) {
                    var dataURL = reader_content.target.result.split(',')[1];
                    var fileName = files[i].name;
                    fileList.push({
                        name: fileName,
                        content: dataURL
                    });
                }
            }
            this.fileList = fileList;
        },

        _onClickUpdateAttachment: function(ev) {
            ev.preventDefault();
            var self = this;
            this.$el.find('#myAttachmentModal').css("display", "none")
            if(self.fileList){
                ajax.jsonRpc('/attachment_proof/submit', 'call', {
                    'partner_id': Number(self.$(ev.currentTarget).attr('value')),
                    'attachments':self.fileList
                }).then(function() {
                    self.fileList = ""
                    self.$el.find("#attachment_proof").val("")

                });
            }
        },

        _onClickShowAttachment: function(ev) {
            var self = this;
            this.$el.find('#updated_attachment').css("display", "block")
            this.$el.find('#vendorScreenBtnShowAttachment').css("display", "none")
            ajax.jsonRpc('/attachment_proof/show_updated', 'call').then(function(attachment_ids) {
                if (attachment_ids.length > 0) {
                    self.$el.find("#showing_updated_vendor_attachment").empty();
                    attachment_ids.forEach(function(attachment) {
                        var id = "/web/content/" + attachment.id;
                        var name = attachment.name;
                        self.$el.find('#showing_updated_vendor_attachment').append("<a class='btn btn-outline-info' href='" + id + "'>" + name + " <i class='fa fa-download'/></a><br/>");
                    });
                } else {
                    self.$el.find("#showing_updated_vendor_attachment").empty();
                    self.$el.find('#showing_updated_vendor_attachment').append("<p style='color: black;'>There are no attachments.</p>");
                }
            });
        }
    })
    PublicWidget.registry.upload_attachment = Template;
    return Template;
})