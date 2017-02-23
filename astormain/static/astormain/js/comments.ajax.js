/**
 * Sending Asynchronous HTTP Request.
 * @param {params} parameters for request etc.
 * @param {callbackDone} callback to call when successfull request
 * @param {callbackFail} callback to call when failure request
 */
function sendRequest(params, callbackDone, callbackFail) {
    if (params === undefined) params = {};
    if (params.url === undefined) {
        throw "Undefined url.";   
    }
    if (params.dataType === undefined) params.dataType = "json";
    if (params.cache === undefined) params.cache = "false";
    if (params.method === undefined) params.method = "GET";

    var csrftoken = getCookie("csrftoken");
    params.beforeSend = function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }

    $.ajax(params)
        .done(callbackDone)
        .fail(callbackFail);
}

/**
 * Add comment to the analysis with specific id.
 * @param {aid} analysis' id
 * @param {body} comment body
 * @param {callbackDone} callback to call when successfull request
 * @param {callbackFail} callback to call when failure request
 */
function addComment(aid, body, callbackDone, callbackFail) {
    if (aid === undefined) {
        throw "Undefined analysis's id.";
    }
    if (body === undefined || body === "") {
        throw "Undefined/empty comment.";
    }
    sendRequest({
        method: "POST",
        url: "/api/analyses/" + aid + "/comments/",
        data: {
            body: body
        }
    }, callbackDone, callbackFail);
}

/**
 * Add reply to the comment with specific id.
 * @param {cid} comment' id
 * @param {body} comment body
 * @param {callbackDone} callback to call when successfull request
 * @param {callbackFail} callback to call when failure request
 */
function addReply(cid, body, callbackDone, callbackFail) {
    if (cid === undefined) {
        throw "Undefined analysis's id.";
    }
    if (body === undefined || body === "") {
        throw "Undefined/empty comment.";
    }
    sendRequest({
        method: "POST",
        url: "/api/comments/" + cid + "/replies/",
        data: {
            body: body
        }
    }, callbackDone, callbackFail);
}

/**
 * Get replies for a comment with specific id.
 * @param {cid} comment' id
 * @param {callbackDone} callback to call when successfull request
 * @param {callbackFail} callback to call when failure request
 */
function getReplies(cid, callbackDone, callbackFail) {
    if (cid === undefined) {
        throw "Undefined comment's id.";
    }
    sendRequest({
        method: "GET",
        url: "/api/comments/" + cid + "/replies/"
    }, callbackDone, callbackFail);
}

/**
 * Get cookie.
 * @param {name} cookie's name
 */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Test whether HTTP method require CSRF protection.
 */
function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}