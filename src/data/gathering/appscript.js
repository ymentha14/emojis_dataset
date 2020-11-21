// App script generating various forms from emoji list

///////////////////////////////////////////////////////////////////////////////////////////// CONSTANTS /////////////////////////////////////////////////////////////////////////////////////////////
var N_CHUNKS = 3

var EMOJIS_CODES = [...Array(12).keys()];
var ASYMPT_CODES = [75,287,1318,446,205,240,540,137]


var FORM_DESC = `
⚠️⚠️⚠️
RANDOM ANSWERING WONT BE REWARDED: SOME OBVIOUS QUESTIONS ONLY HAVE ONE POSSIBLE ANSWER  AND WILL BE CHECKED
⚠️⚠️⚠️

1. You will be presented a list emojis for each of which you need to provide 3 ̲𝖽̲𝗂̲𝗌̲𝗍̲𝗂̲𝗇̲𝖼̲𝗍̲ and ̲𝖺̲𝗉̲𝗉̲𝗋̲𝗈̲𝗉̲𝗋̲𝗂̲𝖺̲𝗍̲𝖾̲ words to describe the emoji, starting from the most representative one to the least representative one. 

2. If you would use an emoji in many contexts, chose the word describing the context the most used first, then the second etc.

Example:
Q0: 🤒
Your answer: "sick,ill,unwell"

• No space between words
• No capital letters
   
The words can be:
• Adjectives (ex:"green", "desesperate")
• Verbs (ex:"cry", "shout")
• Past tense (ex:"worried", "influenced")
𝐍𝐁: keep the original form of the verb (ex: "cry" and not "crying")


3. Two distinct emojis can only have up to 2 words in common, not three.
Example:     👍 --> "cool, ideal, nice"
                     👌 --> "cool, ideal, understood"

4. Use a synonym dictionary to get words as precise as possible. Here are some suggestions
https://www.thesaurus.com/
https://www.merriam-webster.com/thesaurus/dictionary


The fact that certain emojis appear in black and white instead of in color should not affect your opinion, focus on the emotion of the emoji.`


var SINGLE_FORM_DESC = `
⚠️⚠️⚠️
RANDOM ANSWERING WONT BE REWARDED: SOME OBVIOUS QUESTIONS ONLY HAVE ONE POSSIBLE ANSWER  AND WILL BE CHECKED
⚠️⚠️⚠️

1. You will be presented a list emojis for each of which you need to provide the most appropriate word. 

Example:
Q0: 🤒
Your answer: "sick"

• No capital letters
   
The words can be:
• Adjectives (ex:"green", "desesperate")
• Verbs (ex:"cry", "shout")
• Past tense (ex:"worried", "influenced")
𝐍𝐁: keep the original form of the verb (ex: "cry" and not "crying")


4. Use a synonym dictionary to get words as precise as possible. Here are some suggestions
https://www.thesaurus.com/
https://www.merriam-webster.com/thesaurus/dictionary


The fact that certain emojis appear in black and white instead of in color should not affect your opinion, focus on the emotion of the emoji.`


var CONFIRMATION_MSG = `
Thank you for completing our survey! Here is the completion code:

EMOJI389169
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
///////////////////////////////////////////////////////////////////////////////////////////// END HELPER FUNCTIONS /////////////////////////////////////////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////////////////////////////////////// EMOJIS FUNCTIONS /////////////////////////////////////////////////////////////////////////////////////////////

function create_em_field(em_code,form,singleForm=False){
  
  // image insertion
  var folder = DriveApp.getFolderById("16sLvtyPygUbgVWSoAI0t0IYAf-tCIbDQ");
  var imgs = folder.getFiles();
  while (imgs.hasNext()) {
    var img = imgs.next();
    var name = img.getName();
    if (name.split(".")[0] == em_code.toString()) {
      var id = img.getId();
      form.addImageItem()
           .setImage(img)
           .setTitle(em_code.toString());
      break;
    }
  }

  // regex validation
  if (singleForm) {
    var pattern = "^[a-z]+$"
    var helptext = 'Non valid format! "word1" no cap letter'
    } else{
      var pattern = "^[a-z]+,[a-z]+,[a-z]+$"      
      var helptext = 'Non valid format! "(word1,word2,word3)" no cap letter'
      }
  
  var validation = FormApp.createTextValidation()
  .requireTextMatchesPattern(pattern)
  .setHelpText(helptext)
  .build();
 
  form.addTextItem()
  .setTitle(em_code.toString())
  .setRequired(true)
  .setValidation(validation);
}

function createForm(emojis_codes,number,opt_title="",singleForm=false) {
  // Title and description
  if (singleForm){
    var title = "Test Form "+ " single word" +number + opt_title;
    var desc = SINGLE_FORM_DESC 
    } else {
      var title = "Test Form "+ number + opt_title;
      var desc = FORM_DESC
      }
  var form = FormApp.create(title)  
  .setTitle(title)
  .setDescription(desc);
  
  /*
  // Worker ID
  var item = "Worker ID"
  var validation = FormApp.createTextValidation()
  .requireTextMatchesPattern("^[A-Z0-9]*$")
  .setHelpText('MTurk Ids are exclusivels cap letters and numbers.')
  .build();

  form.addTextItem()
  .setTitle(item)
  .setRequired(true)
  .setValidation(validation);
  
  // Subtitle
  form.addSectionHeaderItem().setTitle("Questions")
  
  // Chunkize Emoj
  
  // Emojis Fields
  emojis_codes.forEach(em_code => create_em_field(em_code,form,singleForm))
  
  // Completion text
  form.setConfirmationMessage(CONFIRMATION_MSG)
  
  form.setShowLinkToRespondAgain(false)
  
  */
  var url = form.getPublishedUrl();
  var short_url = form.shortenFormUrl(url)
  short_url = number.toString() + "\t" + short_url
  // shortenFormUrl(url)
  return short_url;
}
///////////////////////////////////////////////////////////////////////////////////////////// END EMOJIS FUNCTIONS /////////////////////////////////////////////////////////////////////////////////////////////


function create_random_forms() {
  shuffleArray(EMOJIS_CODES)
  var emojis_chunk = chunkify(EMOJIS_CODES,N_CHUNKS,true)
  var urls = emojis_chunk.map(function(chunk,i) {return createForm(chunk,i)})
  urls = urls.join("\n");
  var fileName,newFile;//Declare variable names

  fileName = "Test Doc.txt";// a new file name with date on end

  newFile = DriveApp.createFile(fileName,urls);//Create a new text file in the root folder
  
}

function create_asymptotic_form() {
  createForm(ASYMPT_CODES,0," asymptotic pilote")
}

function create_asymptotic_form_1_word() {
    createForm(ASYMPT_CODES,0," asymptotic pilote",true)
    
}

function createGoogleDriveTextFile() {
  var content,fileName,newFile;//Declare variable names
  
  content = "This is the file Content";

  newFile = DriveApp.createFile(fileName,content);//Create a new text file in the root folder
};
