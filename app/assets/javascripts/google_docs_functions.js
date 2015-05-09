function create_new_document(myData){
  var developerKey = 'AIzaSyD9JtT_kVZ0S0vKsskgxrK_WtIE1G7FAjY';
  var clientId = "165043768486-h54df8d1s3id58p9c603q3cq90pe60it.apps.googleusercontent.com"
  var scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file',
  'https://www.googleapis.com/auth/drive.appdata', 'https://www.googleapis.com/auth/drive.apps.readonly'];
  var returnable_link;
  //console.log("WERE HERE AND NEWKEY IS " + item['some_new_thing']);

  gapi.load('auth', {'callback': onAuthApiLoad});
  function onAuthApiLoad() {
    window.gapi.auth.authorize(
        {
          'client_id': clientId,
          'scope': scope,
          'immediate': false
        },
        handleAuthResult);
  }
  function handleAuthResult(authResult) {
    if (authResult && !authResult.error) {
      oauthToken = authResult.access_token; 
      gapi.load('client', function() { 
        gapi.client.load('drive', 'v2', makeRequest); 
      });
    }
  }
  function goodDate(){
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth()+1; //January is 0!
    var yyyy = today.getFullYear();

    if(dd<10) {
        dd='0'+dd
    } 

    if(mm<10) {
        mm='0'+mm
    } 

    today = mm+'/'+dd+'/'+yyyy;
    return today;
  }
  function makeRequest(){
    console.log("making a file request now");
    var url = (window.location.pathname).split("/");
    var id = String(url[url.length - 2]);
    
    var group_name = 'Group #' + String(url[url.length - 1]) + '\'s meeting on ' + goodDate();


    var request = gapi.client.request({
      'path': '/drive/v2/files',
      'method': 'POST',
      'body':{
          "title" : group_name,
          "mimeType" : "application/vnd.google-apps.document",
          "description" : "Document created by Benedict"
       }
   });

    request.execute(function(resp) { 
      //console.log(resp.alternateLink);
      myData['doc_link'] = resp.alternateLink;
      sendBennyReply(JSON.stringify(myData));
    });
  }
  
  
}