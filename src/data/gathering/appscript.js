// App script generating various forms from emoji list

///////////////////////////////////////////////////////////////////////////////////////////// CONSTANTS /////////////////////////////////////////////////////////////////////////////////////////////
var N_CHUNKS = 5

var EMOJIS_CODES = [...Array(50).keys()];

var FORM_DESC = `First things first: please make sure you can properly see the following emojis in your web browser 

TEST EMOJIS:🚝 🚄 🚅 🚈 🚞 🚂 🚆 and that you don't see rectangles instead of emojis. If that is the case, please change browser (firefox works well in general).

⚠️⚠️⚠️
GIVE UP ON THIS QUIZZ IF YOU CANT SEE THE EMOJIS!  YOU WONT BE ABLE TO DECRYPT THE VALIDATION CODE IF YOU CANT PROPERLY SEE THESE EMOJIS.

READ THE GUIDELINE CAREFULLY: FAILING TO RESPECT IT WILL MAKE YOUR SUBMISSION INVALID

RANDOM ANSWERING WONT BE REWARDED: SOME OBVIOUS QUESTIONS ONLY HAVE ONE POSSIBLE ANSWER  AND WILL BE CHECKED
⚠️⚠️⚠️

 You will be presented 24 emojis for each of which you need to provide UP TO 3 ̲𝖽̲𝗂̲𝗌̲𝗍̲𝗂̲𝗇̲𝖼̲𝗍̲ and ̲𝖺̲𝗉̲𝗉̲𝗋̲𝗈̲𝗉̲𝗋̲𝗂̲𝖺̲𝗍̲𝖾̲ words, to describe the emoji, starting from the most representative one to the least representative one. 

Example:
Q0: 🤒
Your answer: "sick,ill,unwell"

The 3 words need to be separated by a "," (comma) with no space.

The words can be:
• Adjectives (ex:"green", "desesperate")
• Verbs (ex:"cry", "shout")
• Past tense (ex:"worried", "influenced")
𝐍𝐁: keep the original form of the verb (ex: "cry" and not "crying")

If you would use an emoji in many contexts, chose the word describing the context the most used first, then the second etc.

Two distinct emojis can only have up to 2 words in common, not three.
Example:     👍 --> "cool, ideal, nice"
                     👌 --> "cool, ideal, understood"

Use a synonym dictionary to get words as precise as possible. Here are some suggestions

https://www.thesaurus.com/
https://www.merriam-webster.com/thesaurus/dictionary


The fact that certain emojis appear in black and white instead of in color should not affect your opinion, focus on the emotion of the emoji.`

var CONFIRMATION_MSG = `
Thank you for completing our survey! Here is the encoded completion code:

! ! ! DO NOT COPY PASTE THE CODE IN MTURK ! ! ! 
EMOJI😾🤡🤠🤬🤢🤐 

You must submit the code "EMOJIXXXXXX" by replacing  the X by the correct number using the following table to decode your completion code :) Thank you for your work!


🤐 = 0 
🤢 = 1
😾 = 3 
🙏 = 2 
👫 = 4
💆 = 5
👵 = 6
🤡 = 7
🤠 = 8
🤬 = 9`
  
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
///////////////////////////////////////////////////////////////////////////////////////////// END HELPER FUNCTIONS /////////////////////////////////////////////////////////////////////////////////////////////


///////////////////////////////////////////////////////////////////////////////////////////// EMOJIS FUNCTIONS /////////////////////////////////////////////////////////////////////////////////////////////

function create_em_field(em_code,form){
  
  // image insertion
  var folder = DriveApp.getFolderById("1PxHWVRpuZIDhr7NPvtmf9p2Ux8gXC0n8");
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
  var validation = FormApp.createTextValidation()
  .requireTextMatchesPattern("^[a-z]+,[a-z]+,[a-z]+$")
  .setHelpText('Non valid format! (word1,word2,word3)')
  .build();
 
  form.addTextItem()
  .setTitle(em_code.toString())
  .setRequired(true)
  .setValidation(validation);
}

function createForm(emojis_codes,number) {
  // Title and description
  var item = "Test Form "+ number;  
  var form = FormApp.create(item)  
  .setTitle(item)
  .setDescription(FORM_DESC);
  
  
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
  emojis_codes.forEach(em_code => create_em_field(em_code,form))
  
  // Completion text
  form.setConfirmationMessage(CONFIRMATION_MSG)
  
  form.setShowLinkToRespondAgain(false)
  
  // shortenFormUrl(url)
}
///////////////////////////////////////////////////////////////////////////////////////////// END EMOJIS FUNCTIONS /////////////////////////////////////////////////////////////////////////////////////////////


function create_forms() {
  shuffleArray(EMOJIS_CODES)
  var emojis_chunk = chunkify(EMOJIS_CODES,N_CHUNKS,true)
  emojis_chunk.forEach( function(chunk,i) {createForm(chunk,i)})
}
