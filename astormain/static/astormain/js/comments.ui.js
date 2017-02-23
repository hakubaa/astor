
$(document).on("click", ".show-reply-form-btn", function() {
    $(this).siblings(".reply-form").show();
    $(this).hide();
    return false;
});

$(document).on("click", ".send-reply-btn", function() {
    var cid = $(this).closest("li").data("cid");
    var body = $(this).siblings(".reply-body").children("textarea").val();
    var $replyForm = $(this).closest(".reply-form");
    var $self = $(this).closest("section");

    if (body === "") {
        alert("Please enter your comment first.");
    } else {
        addReply(
            cid, body,
            function(data, textStatus, jqXHR) {
                var $commentList = $self.children(".commentlist");
                if ($commentList.length == 0) {
                    $commentList = $("<ul class='commentlist'></ul>");
                }
                $commentList.append(createCommentItem(data));
                $self.append($commentList);
                hideReplyForm($replyForm);
            },
            function(jqXHR, textStatus, errorThrown) {
                alert("ERROR");
            }
        );
    }
});

$(document).on("click", ".abort-reply-btn", function() {
    var $replyForm = $(this).closest(".reply-form");
    hideReplyForm($replyForm);
});

$(document).on("click", ".show-replies-btn", function() {
    var cid = $(this).closest("li").data("cid");
    $(this).hide();
    var $self = $(this).closest("section");
    getReplies(
        cid,
        function(comments, textStatus, jqXHR) {
            var $commentList = $self.children(".commentlist");
            if ($commentList.length == 0) {
                $commentList = $("<ul class='commentlist'></ul>");
            }
            for (var i = 0; i < comments.length; i++) {
                $commentList.append(
                    createCommentItem(comments[i])
                );
            }
            $self.append($commentList);
        },
        function(jqXHR, textStatus, errorThrown) {
            alert("ERROR");
        }
    );
    return false;
});

$("#id_send_comment_btn").click(function() {
    var aid = $(this).data("aid");
    var body = $("#id_body").val();
    addComment(
        aid, body, 
        function(data, textStatus, jqXHR) {
            alert("OK");
        },
        function(jqXHR, textStatus, errorThrown) {
            alert("ERROR");
        }
    );
});


/**
 * Hide and clear reply form.
 * @param {replyForm} elemtn to hide
 */
function hideReplyForm(replyForm) {
    replyForm.hide();
    replyForm.find("textarea").val("");
    replyForm.siblings(".show-reply-form-btn").show();    
}

/**
 * Create comments list DOM.
 * @param {comments} object with list of comments
 */
function createCommentList(comments) {
    var $commentList = $("<ul class='commentlist'></ul>");
    for (var i = 0; i < comments.length; i++) {
        $commentList.append(
            createCommentItem(comments[i])
        );
    }
    return $commentList;
}

/**
 * Create comment DOM.
 * @param {comment} object with comment data
 */
function createCommentItem(comment) {
    var $commentItem = $("<li class='comment'></li>");
    $commentItem.data("cid", comment.id);

    var $commentHeader = $(
        "<header class='comment-header'><a href='#'>" + comment.author + 
        "</a> - <span>" + moment(comment.timestamp).format("YYYY-MM-DD HH:mm") + 
        "</span></header>"
    );

    var $commentBody = $(
        "<section class='comment-body'><p>" + comment.body + "</p></section>"
    );

    var $commentReplies = $("<section class='comment-replies'></section>");
    if (is_authenticated()) {
        $commentReplies.append(
            $("<a href='#' class='show-reply-form-btn'>Reply</a>")
        );

        var $replyForm = $("<div></div>", {class: "reply-form"});
        $replyForm.append($(
            "<div class='form-group reply-body'><textarea " +
            "class='form-control' placeholder='Enter your comment.' " +
            "rows='3'></textarea></div>")
        );
        $replyForm.append(
            $("<button class='send-reply-btn'>Send Reply</button>")
        );
        $replyForm.append($("<button class='abort-reply-btn'>Abort</button>"));

        $commentReplies.append($replyForm);
    }
    if (comment.replies.length > 0) {
        $commentReplies.append(
            "<a href='#' class='show-replies-btn'>Show replies (" +
            comment.replies.length +")</a>"
        );
    }

    $commentItem.append($commentHeader);
    $commentItem.append($commentBody);
    $commentItem.append($commentReplies);

    return $commentItem;
}