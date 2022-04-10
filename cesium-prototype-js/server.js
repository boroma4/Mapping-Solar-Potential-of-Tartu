
var express = require('express');
var compression = require('compression');
var areas = require("./public/model/areas.json");

var app = express();
app.use(compression());
app.use(express.static('public'));

var server = app.listen('3000', '0.0.0.0', function () {
    console.log('Application Running: http://localhost:%d', server.address().port);
});

app.get('/areas', function (req, res) {
    res.send(areas)
});

app.get('/area/:id', function (req, res) {
    res.send({area: areas[req.params.id]})
});




