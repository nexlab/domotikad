<?
@include_once("../includes/common.php");
if($GUISUBSECTION=="") {
?>
<script>

var updateUser = function(r) {
  $("#username").text(r.data.username);
  $("#email").val(r.data.email);
  $("#desktophome").val(r.data.desktop_homepath);
  $("#mobilehome").val(r.data.mobile_homepath);
  if(r.data.tts==1)
    $('#tts-switch').bootstrapSwitch('setState', true); //$("#tts").attr('checked', true);
  else
    $('#tts-switch').bootstrapSwitch('setState', false); //$("#tts").attr('checked', false); 
  if(r.data.slide==1)
    $('#slide').bootstrapSwitch('setState', true);
  else
    $('#slide').bootstrapSwitch('setState', false);
  $("#lang").val(r.data.language);
  $("#webspeech").val(r.data.webspeech);
  $("#speechlang").val(r.data.speechlang);
  $("#userform").show();
};


$.get("/rest/v1.2/users/me/json", updateUser);

$("#userform").on("submit", function(event) {
   event.preventDefault();
   if($("#userform input[name=passwd]").val()!=$("#userform input[name=pwd2]").val())
   {
      popupFader('danger', 'ERROR:','Le password inserite non coincidono');
      playTTS('Errore, Le password inserite non coincidono');
   } else {
      $.ajax({url: "/rest/v1.2/users/me/json", type:"PUT", data: $(this).serialize(),
               success: function(res) {
                  popupFader('success', 'SUCCESS:','Utente aggiornato correttamente...');
                  playTTS('Utente aggiornato correttamente');
               },
               error: function(res) {
                  msg=$.parseJSON(res.responseText).data;
                  popupFader('danger', 'ERROR:',msg);
                  playTTS('Errore, utente non aggiornato');
                  $.get("/rest/v1.2/users/me/json", updateUser);
               }
            });
   }
});
<?
}
?>
</script>
