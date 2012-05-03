/**
 * 
 */

function PlotServer(hostname, rocks){
    /*
     * Server class 
     */
    
    // The host hosting plots.
    this.hostname = hostname;
    this.rocks = rocks
    this.current_script = null;
    
    this.get_scripts = function get_scripts(callback) {
        $.getJSON(host + '/available_scripts.json', callback);
    }
    
    this.get_script_info = function get_script_info(script, callback){
        $.getJSON(this.hostname + '/script_help.json?script=' + script, callback);
    } 
    
}

/*
 * Re populate select script with other options.
 */
function populate_scripts(server, selection) {
    
    console.log("populate_scripts!");
    
    select_script = $(selection);
    
    // Rmove options
    select_script.find('option').remove();

    server.get_scripts(function(data) {

        select_script = $(selection);
        select_script.find('option').remove();

        select_script.append('<option value="" >Scripts </option>');
        select_script.append('<option value="" disabled="true" >========</option>');

        for ( var i = 0; i < data.length; i++) {
            var script_doc = data[i];
            var script = script_doc[0];
            var doc = script_doc[1];
            select_script.append('<option value=' + script + '>' + script + ' --- ' + doc.slice(0, 20) + '</option>');
        }
    });

};

function url_changed(form_selector) {
    console.log('url_changed', form_selector);
}

function create_form(server, form_selection) {
    
    var script = server.current_script();
    if (script == '') {
        return;
    }

    console.log("script:" + script);

    server.get_script_info(script, function(data) {

        // $(button_sel).removeAttr("hidden");
    
        form = $(form_selection);
        form.children().remove();
    
        console.log(data);
    
        form.append('<p>' + data.description + '</p>');
    
        args = data.arguments
    
        form.append('<input class="script_form" type="hidden" name="script" value="' + script + '"></input>');
        form_text = '<table>';
    
        for ( var arg in args) {
            form_text += '<tr>';
    
            var deflt = args[arg]['default'];
            var req = args[arg]['required'];
            if (deflt === null) {
                deflt = '';
            }
    
            form_text += '<td>' + arg + ':</td>';
            form_text += '<td>' + args[arg]['help'] + ':</td>';
            if (args[arg]['type'] == 'rock_properties_type') {
                form_text += '<td><select name="' + arg + '" class="script_form rock_selector"><option>Rocks</option><option>==========</option></select></td>';
            } else {
                form_text += '<td><input class="script_form" type="text" name="' + arg + '" value="'
                        + deflt + '"></input></td>';
            }
    
        }
    
        form_text += '</table>';
    
        form.append(form_text);
    
        inputs = form.find('.script_form');
    
        console.log(".script_form", inputs);
        
        inputs.change(server.input_changed);
        inputs.keypress(server.input_changed);
    
        selectors = form.find('.rock_selector');
    
        for (index in server.rocks) {
            rock = server.rocks[index];
            selectors.append('<option value="' + rock.value + '">' + rock.name + '</option>');
        }
    
        server.input_changed();
    });
};

/*
 * Build a query string from a form. @param form: is a jqurey form element.
 */
function build_form_query_string(form) {
    query_string = '?';

    form.find('.script_form').each(function(index) {
        if (index > 0) {
            query_string += '&';
        }

        query_string += this.name + '=' + this.value;

    });

    return query_string;
}

function create_image(url, form_sel) {
    console.log("create_image");

    query_string = build_form_query_string($(form_sel));
    console.log(query_string);
    console.log(url + query_string);
}

function get_rocks(datalist) {
    list_of_rocks = $(datalist).find('option');

    var arr = [];
    list_of_rocks.each(function(index) {
        var name = $(list_of_rocks[index]).attr('data-name');
        var value = $(list_of_rocks[index]).attr('data-value');

        obj = {
            'name' : name,
            'value' : value
        };

        console.log(obj);

        arr.push(obj);
    });

    console.log('arr');
    console.log(arr);
    return arr;
}
