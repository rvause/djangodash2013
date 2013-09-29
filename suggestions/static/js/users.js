$(function () {
    $('a.refresh').on('click', function (e) {
        e.preventDefault();
        $.get($(this).attr('href'), function (data) {
            $('section.current p').html('<s>' + data.suggestion.split_text[0] + '</s><mark>them</mark><s>' + data.suggestion.split_text[1] + '</s>');
            $('section.current').attr('id', data.suggestion.id);
            $('section.current').data('actioned-url', data.suggestion.urls.actioned);
        });
        return false;
    });

    $('section.current p').on('click', 's', function (e) {
        e.preventDefault();
        $.get($(this).parent().parent().data('actioned-url'), function (data) {
            var txt = $('section.current p').text().trim();
            var like_url = $('section.current').data('like-url');
            var likes = $('section.current').data('likes');

            $('section.current').data('like-url', data.suggestion.urls.like);
            $('section.current').attr('id', data.suggestion.id);
            $('section.current').data('likes', data.suggestion.likes);

            $('section.current p').html('<s>' + data.suggestion.split_text[0] + '</s><mark>them</mark><s>' + data.suggestion.split_text[1] + '</s>');
            $('section.current').attr('id', data.suggestion.id);
            $('section.current').data('actioned-url', data.suggestion.urls.actioned);
            $('section.deed.info').after('<section class="deed complete"><p>' + txt + '</p><a href="' + like_url + '" class="icon heart liked">' + likes + '</a></section>');
        });
        return false;
    });
});
