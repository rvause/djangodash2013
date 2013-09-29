var app = app || {};


app.Deed = {
    create: function ( elem, target ) {

    },
    replaceCurrent: function () {

    }
};

app.request = {
    create: function ( elem, user ) {
        var _this     = this;
        this.trigger  = elem;
        trigger.on( 'click', function( e ){
            e.preventDefault();
            _this.getNextDeed( trigger.attr( 'href' ) );
        });
        return this;
    },
    getNextDeed: function ( url ) {
        $.ajax({
            type: 'GET',
            url: url,
            dataType: 'json',
            timeout: 300,
            success: function( data ){
                console.log( data );
            },
            error: function( xhr, type ){
            }
        });

    }
};

var trigger = $('.refresh');
var request = app.request;

request.create( trigger );
