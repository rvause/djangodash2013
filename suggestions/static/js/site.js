var app = app || {};


app.Deed = {
    create: function ( elem, target ) {

    },
    replaceCurrent: function () {

    }
};

app.request = {
    create: function ( elem, active ) {
        var _this   = this;
        this.elem   = elem;
        this.target = active;
        elem.on( 'click', function( e ){
            e.preventDefault();
            _this.getNextDeed( elem.attr( 'href' ) );
        });
        return this;
    },
    getNextDeed: function ( url ) {
        var _this = this;
        $.ajax({
            type: 'GET',
            url: url,
            dataType: 'json',
            timeout: 300,
            beforeSend: function () {
                _this.elem.addClass( 'loading' );
                console.log( _this );
            },
            success: function( data ){
                _this.elem.removeClass( 'loading' );
                _this.updateActiveDeed( data );
            },
            error: function( xhr, type ){
            }
        });
    },
    updateActiveDeed: function ( data ) {
        var $text  = this.target.find('s');
        var $them  = this.target.find( 'mark' );
        var text   = data.split_text;
        var them   = 'them';
        this.target.addClass('finished');
        $text.first().text( text[0] );
        $them.text( them );
        $text.last().text( text[1] );
        this.target.removeClass('finished');
    }
};

var trigger = $('.refresh');
var active  = $('.deed.suggestion');
var request = app.request;

request.create( trigger, active );
