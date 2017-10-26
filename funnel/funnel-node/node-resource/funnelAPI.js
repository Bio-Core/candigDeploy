var http = require ('http');
var request = require ('request')
var config = require ('./config.json')

// template for getting job, joblist, worker, workerlist, etc info
var getInfo = function (url, callback) {
    http.get(url, function (response) {
        var body = '';
        response.on('data', function(d) {body += d;});
        response.on('end', function() {callback.send(body)})
    })
}

// worker and worker list
exports.getWorkerList = function (callback) {
    var url = config.funnelURL + '/v1/funnel/workers';
    console.log (url);
    getInfo (url, callback);
}

// job and job list
exports.getJobList = function (callback) {    
    var url = config.funnelURL + '/v1/tasks';
    getInfo (url, callback);
}

exports.getJob = function (job_id, callback) {
    var url = config.funnelURL + '/v1/tasks/' + job_id;
    console.log (url);
    getInfo (url, callback);
}

exports.deleteJob = function (job_id) {
    var url = config.funnelURL + '/v1/tasks/' + job_id;
    console.log (url);
    var options = {
        url: url,
        method: 'DELETE'
    }    
    request(options, function (error, response, body) {
        if (!error && response.statusCode == 200) {
            console.log(body)
        }
    })       
    // http.delete(url);
}

// submit jobs
exports.submitJob = function (data) {
    console.log (data)
    var funnelURL = config.funnelURL + '/v1/tasks'
    var headers = {
        'User-Agent':       'Super Agent/0.0.1',
        'Content-Type':     'application/json'
    }
    
    var options = {
        url: funnelURL,
        method: 'POST',
        headers: headers,
        body: data
    }    
    request(options, function (error, response, body) {
        if (!error && response.statusCode == 200) {
            // Print out the response body
            console.log(body)
        }
    })    
}