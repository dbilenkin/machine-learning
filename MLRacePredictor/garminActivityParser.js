const request = require('request');
const fs = require('fs');


// Set the headers
var headers = {
    'User-Agent':       'Super Agent/0.0.1',
    'Content-Type':     'application/x-www-form-urlencoded'
}

//Configure the request
var options = {
    url: 'https://connect.garmin.com/modern/proxy/activitylist-service/activities/jeffdnapoli',
    method: 'GET',
    headers: headers,
    qs: {'start': '1', 'limit': '500'}
}

// Configure the request
var options = {
    url: 'jeffActivities.json',
    method: 'GET'
}

// Start the request
// request(options, function (error, response, body) {
//     if (!error && response.statusCode == 200) {
//         // Print out the response body
//         parseActivities(JSON.parse(body))
//     }
// })

function createActivityData(activity) {
    let activityData = {};
    activityData.date = new Date(activity.startTimeLocal.split(" ")[0]);
    activityData.activityType = activity.activityType.typeKey;
    activityData.distance = activity.distance;
    activityData.duration = activity.duration;
    return activityData
}

function parseActivities(json, start, end) {
    
    const activities = json['activityList'];
    console.log(activities.length);

    const dateFilteredActivities = activities.filter(activity => {
        return activity.startTimeLocal < end && activity.startTimeLocal > start;
    }).map(createActivityData);

    console.log(dateFilteredActivities[0]);
    console.log(dateFilteredActivities[dateFilteredActivities.length-1]);

    return dateFilteredActivities;

}

function fairlyClose(source, target) {
    const offBy = Math.abs(source - target)/source;
    
    if (offBy < .05) {
        console.log("source: " + source + ", off By: " + offBy);
        return true;
    }
    return false;
}

function findRecord(activities, distance, duration) {
    const records = activities.filter(activity => {
        return fairlyClose(activity.distance, distance) && fairlyClose(activity.duration, duration);
    })

    if (records && records.length == 1) {
        return records[0];
    } else {
        return null;
    }
}

const activitiesJson = JSON.parse(fs.readFileSync('jeffActivities.json', 'utf8'));
const dateFilteredActivities2016 = parseActivities(activitiesJson, "2016-01-01", "2017-01-01");

//Jeff's 5k record in 2017
const fiveKrecord = findRecord(dateFilteredActivities2016, 5000, 22*60+10);
console.log(fiveKrecord);

const dateFilteredActivities2017 = parseActivities(activitiesJson, "2017-01-01", "2018-01-01");
//Jeff's 5k record in 2017
const tenKrecord = findRecord(dateFilteredActivities2017, 10000, 47*60+29);

console.log(tenKrecord);

