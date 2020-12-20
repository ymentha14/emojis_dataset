// App script generating various forms from emoji list

///////////////////////////////////////////////////////////////////////////////////////////// CONSTANTS /////////////////////////////////////////////////////////////////////////////////////////////
var N_FORMS = 133 //final number of forms
var N_FORMS_DEBUG = 3 //number of forms to keep for debugging
var SELECTED_INDEXES_URL = "https://docs.google.com/document/d/1P7q1hgBrlRqpnATcnHZxMrlRuKzxQx0pj3ab4iqexYM/edit"; // id of a gdoc containing the indexes of the selected emojis
var HONEY_POTS_INDEXES = [3006, 3091, 2897, 2282, 451, 2280, 613, 387, 740, 597, 846, 3059, 1284, 444, 2528, 2640, 2885, 1095, 2533, 828, 699] // index of the honeypots emojis
var FORM_DESC_URL = "https://docs.google.com/document/d/1Lw4uUvqNk3zgijdvszpcR7L5FF4eC7AQREIoFHrvsKM/edit"; // id of the gdoc containing the description of the form
var IDX2URL_FILENAME = "forms_url.txt"
var FEEDBACK_HELP_TEXT = "You can optionally give us feedback about the HIT. We value your feedback as it allows us to improve our surveys. The feedback can concern anything about the Google form or the MTurk HIT."
var WORKERID_HELP_TEXT = "Enter your worker id here: IMPORTANT make sure it is correctly spelled as this will allow us to map your work to your mturk account and validate your HIT."
var CONFIRMATION_MSG = `
🎉🎉Thank you for completing our survey!🎉🎉
Here is your MTurk completion code. Either copy-paste it or enter the 3 numbers with no space in the required field on the mturk HIT page you come from.


`
///////////////////////////////////////////////////////////////////////////////////////////// END CONSTANTS /////////////////////////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////////////////////// HELPER FUNCTIONS /////////////////////////////////////////////////////////////////////////////////////////////

function chunkify(a, n, balanced) {
  if (n < 2)
    return [a];
  var len = a.length,
      out = [],
      i = 0,
      size;
  if (len % n === 0) {
    size = Math.floor(len / n);
    while (i < len) {
      out.push(a.slice(i, i += size));
    }
  }
  else if (balanced) {
    while (i < len) {
      size = Math.ceil((len - i) / n--);
      out.push(a.slice(i, i += size));
    }
  }
  else {
    n--;
    size = Math.floor(len / n);
    if (len % size === 0)
      size--;
    while (i < size * n) {
      out.push(a.slice(i, i += size));
    }
    out.push(a.slice(size * n));
  }
  return out;
}

function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

function generate_password(i) {
  var a = i * 324 + 932;
  return a.toString().substr(0,3)
}

function read_gdoc(url) {
  /* read a google doc as a string from its url*/
  var doc = DocumentApp.openByUrl(url);
  var datastring = doc.getBody().getText();
  return datastring
}

function get_next_form_idx() {
  folder = DriveApp.getRootFolder()
  /* determine which form needs to be created according
  to the ones already generated */
  var idxes = []
  var files = folder.getFiles();
  while (files.hasNext()) {
    var file = files.next();
    var name = file.getName();
    if (name.startsWith("Test Form")){
      name = name.split(" ")
      idx = name[name.length-1]
      idxes.push(idx)
    }
  }
  if (idxes.length == 0){
    return 0
  }
  var max_idx = Math.max.apply(Math,idxes)
  return max_idx + 1
}

function createorappend2file(formidx,fileName,content) {
  if (formidx == 0){
    newFile = DriveApp.createFile(fileName,content);//Create a new text file in the root folder
  }
  else {
    var folder = DriveApp.getRootFolder()
    var fileList = folder.getFilesByName(fileName);
    if (fileList.hasNext()) {
      // found matching file - append text
      var file = fileList.next();
      var combinedContent = file.getBlob().getDataAsString() + "\n" + content;
      file.setContent(combinedContent);
    }
  }
}

function insert_in_middle(array,element) {
  var n = array.length
  var middle = Math.floor(n/2)
  var pre = array.slice(0,middle)
  var post = array.slice(middle)
  var tot = pre.concat([element]).concat(post)
  return tot
}


///////////////////////////////////////////////////////////////////////////////////////////// END HELPER FUNCTIONS /////////////////////////////////////////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////////////////////////////////////// EMOJIS FUNCTIONS /////////////////////////////////////////////////////////////////////////////////////////////

function add_demographic(form,title_base){
  
  // Demographic
  form.addSectionHeaderItem()
  .setTitle("User informations")
  .setHelpText("If you already provided your user information (Age, Gender, and Mothertongue) in a previous HIT '" + title_base + "', you can leave it blank.");
  
  // Age
  var agevalidation = FormApp.createTextValidation()
  .requireTextMatchesPattern("^[0-9]{2}$")
  .setHelpText('Only digits for the age (ex: "26")')
  .build();
  
  form.addTextItem()
  .setTitle("Age")
  .setHelpText("Your age")
  .setValidation(agevalidation)
  .setRequired(false)

  // Gender  
  var genderitem = form.addMultipleChoiceItem()
  genderitem.setTitle("Gender")
  .setChoices([
        genderitem.createChoice('Male'),
        genderitem.createChoice('Female'),
        genderitem.createChoice('Other')
     ])
  .setHelpText("Your gender")
  .setRequired(false)
 
  // Mothertongue
  var lanvalidation = FormApp.createTextValidation()
  .requireTextMatchesPattern("^[a-z]+$")
  .setHelpText('only lowercase letters (ex: english)')
  .build();
  
  form.addTextItem()
  .setTitle("Mothertongue")
  .setHelpText("Your mothertongue")
  .setValidation(lanvalidation)
  .setRequired(false)
  
}

function create_em_field(em_code,form,singleForm=False){
  /**
 * Summary. (use period)
 * @param {int}    em_code       Index of the emoji.
 * @param {gform}  form          Form in which writing the emoji field
 * @param {bool}   singleForm    Whether to allow only for one word in the validation
 */
  var img_title = em_code.toString() + ".png"

  // image insertion
  var folder = DriveApp.getFolderById("1uPqVyfp_DkOMEqm7_zRyjpDAHycgpu94");
  var imgs = folder.searchFiles('title = "' + img_title + '"')
  var img = imgs.next();
  var check = imgs.hasNext()
  form.addImageItem()
           .setImage(img)
           .setTitle(em_code.toString());

  // regex validation
  if (singleForm) {
    var pattern = "^[a-z]+$"
    var helptext = 'Non valid format! Only lower-case letters a-z'
    } else{
      var pattern = "^[a-z]+,[a-z]+,[a-z]+$"
      var helptext = 'Non valid format! "(word1,word2,word3)" no cap letter'
      }

  var validation = FormApp.createTextValidation()
  .requireTextMatchesPattern(pattern)
  .setHelpText(helptext)
  .build();

  form.addTextItem()
  .setTitle(em_code.toString() + " (emoji above)")
  .setRequired(true)
  .setValidation(validation);
}

function createForm(emojis_codes,formidx,opt_title="",singleForm=false) {
  /* Create a google form

  Args:
  emojis_codes (list of int): list of the indexes of the emojis present in the form
  number (int): index of the form
  opt_title (str): optional title to add
  singleForm (Bool): whether to accept a single word per emoji (3 otherwise)
  */

  // Title and description
  var title_base = "Test Form "
  if (singleForm){
    var title = title_base + formidx + opt_title;
    } else {
      var title = title_base + " three words " +formidx + opt_title;
    }
  var desc = read_gdoc(FORM_DESC_URL)

  var form = FormApp.create(title)
  .setTitle(title)
  .setDescription(desc);


  // Worker ID
  var item = "Worker ID"
  var validation = FormApp.createTextValidation()
  .requireTextMatchesPattern("^A[A-Z0-9]+$")
  .setHelpText('MTurk Ids are exclusivels cap letters and numbers.')
  .build();

  form.addTextItem()
  .setTitle(item)
  .setRequired(true)
  .setValidation(validation)
  .setHelpText(WORKERID_HELP_TEXT)
  ;
  
  // Demographic infos
  add_demographic(form,title_base)
 
  // Subtitle
  form.addSectionHeaderItem()
  .setTitle("Questions")

  // Honeypot 
  // TODO: ensure the honeypot is not already present in the form
  var honey_emoji_idx = HONEY_POTS_INDEXES[formidx % HONEY_POTS_INDEXES.length]
  emojis_codes =  insert_in_middle(emojis_codes,honey_emoji_idx)
  
  // Emojis Fields
  emojis_codes.forEach(em_code => create_em_field(em_code,form,singleForm))
  
  // Feedback field
  form.addTextItem()
  .setTitle("Feedback")
  .setHelpText(FEEDBACK_HELP_TEXT)
  .setRequired(false)

  // Completion
  var password = generate_password(formidx);
  form.setConfirmationMessage(CONFIRMATION_MSG + password)

  form.setShowLinkToRespondAgain(false)

  // Update the form's response destination
  var ss = SpreadsheetApp.create('form_result_'+formidx.toString());
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId())
  var res_url = ss.getUrl();


  var url = form.getPublishedUrl();
  var short_url = form.shortenFormUrl(url)
  short_url = formidx.toString() + "," + short_url + "," + res_url
  createorappend2file(formidx,IDX2URL_FILENAME,short_url)
}
/////////////////////////You can optionally provide us with a feeback concerning the HIT: we value these feedbacks as they allow us to improve our surveys. The feedback can concern anything about the google forms/ Mturk hit.//////////////////////////////////////////////////////////////////// END EMOJIS FUNCTIONS /////////////////////////////////////////////////////////////////////////////////////////////

function create_honey_forms() {
  var form_idx = 4
  emojis_codes = chunkify(HONEY_POTS_INDEXES,2,true)
  emojis_codes.map(function(chunk,i) {return createForm(chunk,i,"",true)})
};

function create_random_forms() {
  var next_form_idx = get_next_form_idx();
  var emojis_codes = eval(read_gdoc(SELECTED_INDEXES_URL))
  //shuffleArray(emojis_codes)
  emojis_codes = chunkify(emojis_codes,N_FORMS,true)
  // we only care for the next N_FORMS_DEBUG forms
  emojis_codes = emojis_codes.slice(next_form_idx,next_form_idx+N_FORMS_DEBUG)

  emojis_codes.map(function(chunk,i) {return createForm(chunk,i+next_form_idx,"",true)})

};

function create_single_form() {
  var form_idx = 4
  var emojis_codes = eval(read_gdoc(SELECTED_INDEXES_URL))
  //shuffleArray(emojis_codes)
  emojis_codes = chunkify(emojis_codes,N_FORMS,true)
  // we only care for the next N_FORMS_DEBUG forms
  emojis_codes = emojis_codes.slice(form_idx,form_idx+1)
  emojis_codes.map(function(chunk,i) {return createForm(chunk,i+next_form_idx,"",true)})
};

