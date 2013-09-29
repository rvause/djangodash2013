var app = app || {};


app.Deed = {
    create: function ( elem, target, parent ) {
        var _this   = this;
        this.elem   = elem;
        this.target = active;
        this.parent = parent;
        elem.on( 'click', function ( e ) {
            e.preventDefault();
        });
        return this;
    },
    replaceCurrent: function () {

    }
};

app.anonRequest = {
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
                _this.updateCurrentDeed( data );
            },
            error: function( xhr, type ){
            }
        });
    },
    updateCurrentDeed: function ( data ) {
        var $text  = this.target.find( 's' ),
            $them  = this.target.find( 'mark' );
        this.target.addClass( 'complete' );
        $text.first().text( $.trim( data.split_text[ 0 ] ) );
        $text.last().text(  $.trim( data.split_text[ 1 ]  ) );
        this.target.removeClass( 'complete' );
    }
};

app.userRequest = {
};

var anonRequest = app.anonRequest;
anonRequest.create( $('.refresh'), $('.deed.current') );
