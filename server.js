var http = require('http');
var fs = require('fs');
var path = require('path');
var mysql = require('mysql');

var con = mysql.createConnection({
  host: "127.0.0.1",
  port: 8889,
  user: "root",
  password: "root",
  database: "cash_system"
});


con.connect(function(err) {
    if (err) throw err;
    else console.log("Connected!");

http.createServer(function (request, response) {
    var address_path = request.url.toString();
    address_path = address_path.substring(1,address_path.length)

    con.query("SELECT * from links WHERE random_string = ?",[address_path], function (err, result) {
        if (err) throw err;
        console.log(result)
        if(result.length == 1){
            if(result[0].is_used == 0){     //// TODO: add timestamp comparison

     
    /// TODO: request, if address_path is valid and not used

      
    var filePath = './receipts' + request.url;
    // if (filePath == './')
    //     filePath = './';

    var extname = path.extname(filePath);
    var contentType = 'text/html';
    switch (extname) {
        case '.pdf':
            contentType = 'application/pdf';
            break;        
    }

    fs.readFile(filePath, function(error, content) {
        if (error) {
            if(error.code == 'ENOENT'){
                fs.readFile('./404.html', function(error, content) {
                    response.writeHead(200, { 'Content-Type': contentType });
                    response.end(content, 'utf-8');
                });
            }
            else {
                response.writeHead(500);
                response.end('Sorry, check with the site admin for error: '+error.code+' ..\n');
                response.end(); 
            }
        }
        else {
            response.writeHead(200, { 'Content-Type': contentType });
            response.end(content, 'utf-8');
        }
        con.query("UPDATE links SET is_used = 1 WHERE random_string = ?",[address_path], function (err, result) {
            if (err) throw err;
        });
    });
    } else {
        response.end("No Access");
    }
    } else {
        response.end("Error");
    }
    });

}).listen(8125);
});
console.log('Server running at http://127.0.0.1:8125/');