// function to get the row onclick event 

$('.dataframe').on('click', 'tr', function(e){
    tableText($(this).html());
  });
  
  function tableText(tableRow) {
    var myJSON = JSON.stringify(tableRow);
    console.log(myJSON);
  }

// function to take the row data to the deets page using url parameters
// deets to include: the date, and the name of the fighters

// insert unique css classes into the odds tables

// for odds tables that don't have a model attached, include a button
// that binds to the specific odds table

// write a function that gets all the child td tags that is called on button click
// using QuerySelectAll()