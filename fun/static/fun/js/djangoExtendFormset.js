;(function initExtendFormsetPlugin($, window, undefined) {
    "use strict";
    /*
    jQuery plugin to dynamically extend Django formset by cloning last form and incrementing counters
    Also handle deletion and ordering
    Author: Richard Moch
    Version: 1.0.0 (May 2013)
    Licensed under the MIT license:
    http://www.opensource.org/licenses/mit-license.php
        $('#table-id').extendFormset({
                'prefix': 'formset',             // formset name, will be used to prefix all fields
                'clone_selector': 'tr',          // selector of element to clone to create new form
                'add_button_class': '',          // css class of the button added beside the formset to add a form
                'add_button_value': 'Add';       // label of the button
                'callback':                      // function to call with the newly created element
                'handle_order': true,            // handle order field
                'reindex_order': true,           // reindex from 0
                'handle_delete': true,           // replace delete check box by html element button
                'delete_button': '<i class="icon icon-trash"></i>'  // delete button's html
        })
    */

    var defaults = {
        'prefix': '',
        'clone_selector': 'tr',  // by default, clone a table's tr
        'callback': undefined,
        'add_button_class': 'btn btn-primary',    // Add form button classes
        'add_button_value': "Add",
        'add_button_container': undefined,
        'handle_order': true,
        'reindex_order': true,
        'handle_delete': true,
        'delete_button': '<i class="icon icon-trash"></i>'  // Delete form button content
    };

    function ExtendFormsetPlugin(element, options) {
        this.element = element;
        this.$element = $(element);

        this.refElement = null;
        this.regexp = /-[\d]+-/;
        this.pattern = '-X-';
        this.options = $.extend( {}, defaults, options);
        this._defaults = defaults;
        this.init();
    }

    // Initialization.
    ExtendFormsetPlugin.prototype.init = function() {
        var self = this;
        // add button after this.$element
        var button_id = 'add-form-' + self.options.prefix;
        var container = self.options.add_button_container || self.$element;
        console.log(container);
        $(container).after($('<input>').attr({
                'type': 'button',
                'value': self.options.add_button_value,
                'id': button_id,
                'class': self.options.add_button_class
        }));
        self.refElement = self.$element.find(self.options.clone_selector + ':last').clone(true);

        var total = $('[name^="' + this.options.prefix + '"][name$="TOTAL_FORMS"]').val();
        self.refElement.find(':input').each(function() {
            var real_name = $(this).attr('name').split('-')[2];
            $(this).attr('name', $(this).attr('name').replace(self.regexp, self.pattern));
        });

        if (self.options.handle_delete) {
            self.deleteButton(self.refElement);
            self.deleteButton(self.element);
        }


        $('#' + button_id).click(function() {
            var newElement = self.cloneElement();
            if (self.options.callback) {
                self.options.callback(newElement);
            }
        });

        if (self.options.handle_order && self.options.reindex_order) {
            // reindex order fields
            var order = 0;
            $('input[name$="-order"]').each(function(){
                $(this).attr('value', order);
                order += 1;
            });
        }
    };

    ExtendFormsetPlugin.prototype.deleteButton = function(element) {
        // If we have checkboxes for deletion, hide and replace with a nice button.
        // In case of form validation fail, a delete checkbox which was previously checked
        // will return checked which is stupid and blocking in our case, so we reset checked ones
        var self = this;
        $(element).find('input[type="checkbox"][name$="-DELETE"]').each(function(){
            var parent = $(this).parent();
            var hidden = $('<input>').attr({
                    'type': 'hidden',
                    'name': $(this).attr('name'),
                    'value': ''});  // whatever its value reset checkbox
            $(parent).append(hidden);
            $(this).remove();
            $(parent).append($('<span>').attr({'class': 'btn'}).click(function (){
                $(hidden).attr('value', 'checked');
                var ele = $(this).closest(self.options.clone_selector);
                $(ele).fadeOut();
            }).html(self.options.delete_button));
        });
    };

    ExtendFormsetPlugin.prototype.cloneElement = function() {
        /* clone a given element and increment form index */
        var self = this;
        var newElement = self.refElement.clone(true);
        var total = $('[name^="' + this.options.prefix + '"][name$="TOTAL_FORMS"]').val();
        newElement.find(':input').each(function() {

            var real_name = $(this).attr('name').split('-')[2];
            var name = $(this).attr('name').replace(self.pattern, '-' + total + '-');
            var id = 'id_' + name;
            var value = '';
            if (real_name == 'order' && self.options.handle_order) {
                value = $('input[name$="-order"]').length;
            }
            $(this).attr({'name': name, 'id': id});
            if ($(this).is('[value]')) {  // checkbox do not have 'value' attribute, but will answer 'on' to $.attr()
                $(this).val(value);
            }
        });
        // rename html labels 'for' attribute if necessary
        newElement.find('label').each(function() {
            if ($(this).attr('for') !== undefined) {
                var newFor = $(this).attr('for').replace(self.pattern, '-' + total + '-');
                $(this).attr('for', newFor);
            }
        });

        total++;
        $('[name^="' + this.options.prefix + '"][name$="TOTAL_FORMS"]').val(total);
        $(self.$element.find(self.options.clone_selector + ':last')).after(newElement);
        return newElement;
    };

    $.fn.extendFormset = function extendFormset(option) {
        // Prevent multiple instantiations by setting plugin instance to it's own DOM element
        return this.each(function() {
            var $this = $(this);
            var data = $this.data('extendFormsetInstance');
            var options = typeof option === 'object' && option;
            if (!data) {
                $this.data('extendFormsetInstance', (data = new ExtendFormsetPlugin(this, options)));
            }
            if (typeof option === 'string') {
                data[option]();
            }
        });
    };
}(jQuery, window));