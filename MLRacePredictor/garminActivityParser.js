const request = require("request");
const fs = require("fs");
const csv = require("fast-csv");

// Set the headers

var headers = {
  "User-Agent": "Super Agent/0.0.1",
  "Content-Type": "application/x-www-form-urlencoded"
};

//Configure the request

var options = {
  url: "",
  method: "GET",
  headers: headers,
  qs: { start: "1", limit: "1000" }
};

// Configure the request

// var options = {
//   url: "jeffActivities.json",
//   method: "GET"
// };

var runningData = [];
var goodData = [];
var users = {};

var csvStream;
var writableStream;

function readDataCSV() {
  var stream = fs.createReadStream("data.csv");

  csv
    .fromStream(stream, { headers: true })
    .on("data", function(data) {
      runningData.push(data);
      //console.log(data);
    })
    .on("end", function() {
      getDataForUsers();
    });
}

function createWriteStream() {
  csvStream = csv.createWriteStream({ headers: true });
  writableStream = fs.createWriteStream("goodData.csv");

  writableStream.on("finish", function() {
    console.log("DONE!");
  });

  csvStream.pipe(writableStream);
  //goodData.forEach(a => csvStream.write(a));
}

function removeDuplicates(myArr, prop) {
  return myArr.filter((obj, pos, arr) => {
    return arr.map(mapObj => mapObj[prop]).indexOf(obj[prop]) === pos;
  });
}

function getDataForUsers() {
  runningData = removeDuplicates(runningData, "user");
  runningData = runningData.filter(a => a.marathonYear > "2010");
  getNextUser(runningData, 0);
}

function secondsToTimeString(seconds) {
  var hours = Math.floor(seconds / 3600);
  var minutes = Math.floor((seconds % 3600) / 60);
  seconds = seconds % 60;
  return hours + ":" + minutes + ":" + seconds;
}

function timeStringToSeconds(timeString) {
  var t = timeString.split(":");
  if (t.length === 3) {
    var seconds = parseInt(t[0]) * 3600 + parseInt(t[1]) * 60 + parseInt(t[2]);
  } else {
    var seconds = parseInt(t[0]) * 60 + parseInt(t[1]);
  }
  
  return seconds;
}

function getNextUser(runningData, count) {
  if (count >= runningData.length) {
    csvStream.end();
    return;
  }
  var user = runningData[count].user;
  options.url =
    "https://connect.garmin.com/modern/proxy/activitylist-service/activities/" +
    user;
  request(options, function(error, response, body) {
    if (!error && response.statusCode == 200) {
      var userData = runningData.filter(a => a.user === user)[0];
      var activities = parseActivities(
        JSON.parse(body),
        "2009-01-01",
        "2019-01-01"
      );
      getCommonRecords(userData, activities);
    } else {
      console.log("ERROR: " + body);
    }
    count++;
    getNextUser(runningData, count);
  });
}

function getCommonRecords(userData, activities) {
  commonDistances = {
    "marathon": 42195,
    "half": 21097,
    "10K": 10000,
    "5K": 5000
  };

  for (var name in commonDistances) {
    var distance = commonDistances[name];
    var record = findFastestByDistance(activities, distance);
    userData[name + "Record"] = secondsToTimeString(record.duration);
    if (
      fairlyClose(
        record.duration,
        timeStringToSeconds(userData[name])
      )
    ) {
      console.log(name.toUpperCase() + " RECORD FOUND!!!");

      [3, 12].forEach(numMonths => {
        const totals = getLastMonths(activities, record, numMonths);
        console.log("average monthly miles: " + totals.distance / 1609.34 / numMonths);

        userData[name + "TrainDis" + numMonths] = totals.distance / 1609.34 / numMonths;

        var secondsPerMile = totals.duration / (totals.distance / 1609.34);
        console.log(secondsPerMile);

        var minutes = Math.floor(secondsPerMile / 60);
        var seconds = secondsPerMile % 60;
        console.log("average pace: " + minutes + ":" + seconds);

        userData[name + "TrainPace" + numMonths] = minutes + ":" + seconds;
        userData[name + "TrainPaceSec" + numMonths] = secondsPerMile;
        userData[name + "TrainDays" + numMonths] = totals.activityCount;
      });

      userData[name + "Date"] = record.date.toISOString().split('T')[0];

    } else {
      [3, 12].forEach(numMonths => {
        userData[name + "TrainDis" + numMonths] = 0;
        userData[name + "TrainPace" + numMonths] = 0;
        userData[name + "TrainPaceSec" + numMonths] = 0;
        userData[name + "TrainDays" + numMonths] = 0;

      });
      userData[name + "Date"] = 'null';
    }
  }
  goodData.push(userData);
  csvStream.write(userData);
  console.log(userData);
}

function createActivityData(activity) {
  var activityData = {};
  activityData.date = new Date(activity.startTimeLocal.split(" ")[0]);
  activityData.activityType = activity.activityType.typeKey;
  activityData.distance = activity.distance;
  activityData.duration = activity.duration;
  return activityData;
}

function parseActivities(json, start, end) {
  const activities = json["activityList"];

  const dateFilteredActivities = activities
    .filter(a => a.startTimeLocal < end && a.startTimeLocal > start)
    .filter(a => a.activityType.typeKey === "running")
    .map(createActivityData);

  return dateFilteredActivities;
}

function fairlyClose(source, target) {
  return Math.abs(source - target) / source < 0.01;
}

function findRecord(activities, distance, duration) {
  const records = activities.filter(activity => {
    return (
      fairlyClose(activity.distance, distance) &&
      fairlyClose(activity.duration, duration)
    );
  });

  if (records && records.length == 1) {
    return records[0];
  } else {
    return null;
  }
}

function getLastMonths(activities, activity, months) {
  var startDate = new Date(activity.date);
  startDate.setMonth(startDate.getMonth() - months);
  const dateFilteredActivities = activities.filter(a => {
    return a.date < activity.date && a.date > startDate;
  });

  var totals = {
    distance: 0,
    duration: 0,
    activityCount: 0
  };

  dateFilteredActivities.forEach(a => {
    totals.distance += a.distance;
    totals.duration += a.duration;
    totals.activityCount++;
  });

  return totals;
}

function findFastestByDistance(activities, distance) {
  var fastest = {
    duration: 1000000000,
    distance: 0
  };

  var adjDistance = distance * 0.99;
  activities.forEach(activity => {
    if (
      activity.distance > adjDistance &&
      activity.duration < fastest.duration
    ) {
      fastest = activity;
    }
  });

  return fastest;
}

createWriteStream();
readDataCSV();

// const activitiesJson = JSON.parse(
//   fs.readFileSync("jeffActivities.json", "utf8")
// );

// const dateFilteredActivities = parseActivities(
//   activitiesJson,
//   "2010-01-01",
//   "2019-01-01"
// );

//Jeff's 5k record in 2017

// const fiveKrecord = findFastestByDistance(dateFilteredActivities, 5000);
// console.log("5K: " + JSON.stringify(fiveKrecord));

// //Jeff's marathon record in 2017

// const marathonRecord = findFastestByDistance(dateFilteredActivities, 42195);
// console.log("marathon: " + JSON.stringify(marathonRecord));

// const totals = getLastThreeMonths(dateFilteredActivities, marathonRecord);
// console.log("average monthly miles: " + totals.distance / 1609.34 / 3);

// var secondsPerMile = totals.duration / (totals.distance / 1609.34);
// console.log(secondsPerMile);

// var minutes = Math.floor(secondsPerMile / 60);
// var seconds = secondsPerMile % 60;
// console.log("average pace: " + minutes + ":" + seconds);

// console.log("totals: " + JSON.stringify(totals));
