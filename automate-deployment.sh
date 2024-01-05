alias genai="h2o --conf ~/.h2oai/haic-genai-appstore.toml"

update() {
  echo "Checking if there's a new version of $1"
  new_app_version=$(toml get --toml-path ./$3/app.toml App.Version)

  if grep -q $new_app_version <<< "$(genai admin app list --name $1 -l)"; then
      echo "The local and deployed apps have the same app version"
      # move on to the next app
  else
      echo "The local app is a new version"

      echo "Fetching IDs of previous app version"
      old_app_id=$(genai admin app list --name $1 -l | awk 'NR==2{print $1}');

      echo "Importing the new app version"
      cd $3 && genai bundle import -v PUBLIC && cd ../;
      if test $? -ne 0 ; then
        cd ../;
        return 1;
      fi

      new_app_id=$(genai admin app list --name $1 -l | awk 'NR==2{print $1}');

      if test "$1" != "ai.h2o.link.h2ogpte"; then
        # The app is not a link app, which means we need to run instances and assign aliases
        # if this repo ends up with a lot of link apps we could do something better like check if the toml is link

        echo "Fetching IDs of previous app instance"
        old_instance_id=$(genai admin instance list $old_app_id | awk 'NR==2{print $1}');

        echo "Running an instance of the new app version"
        new_instance_id=$(genai app run $new_app_id -v ALL_USERS | awk 'NR==1{print $2}');

        echo "Assigning the alias to the new app version"
        genai admin alias assign $2 $new_instance_id True;

        echo "Privating the previous instance - do not delete without testing!!"
        genai admin instance update -v PRIVATE $old_instance_id
      fi

      echo "Privating the previous app version - do not delete without testing!!"
      genai admin admin app update -v PRIVATE $old_app_id
  fi
}

# App Name from app.toml, alias pre-created in genai.h2o.ai, folder name in github
update "ai.h2o.wave.ask_h2o" "ask-h2o" "ask-h2o";
update "ai.h2o.wave.brazil-lawgpt" "brlawgpt" "brlawgpt";
update "ai.h2o.demo.CallCenterGPT_aistore" "call-center" "CallCenterGPT";
update "ai.h2o.wave.company_info_at_a_glance" "company-info-at-a-glance" "company-financial-overview";
update "ai.h2o.wave.cycling_training_plan" "cycling" "cycling-training-plan";
update "ai.h2o.wave.investment-research" "financial-research" "financial-research";
update "ai.h2o.wave.grammar_and_syntax_review" "content-review" "grammar-and-syntax-review";
update "ai.h2o.link.h2ogpte" "" "h2ogpte-link";
update "ai.h2o.wave.make_home_listing" "make-home-listing" "home-listings";
update "ai.h2o.wave.bingo_new_years_cards" "2024-bingo" "new-year-bingo-card";
update "ai.h2o.wave.clean-code-inspector" "python" "python-code-inspector";
update "ai.h2o.wave.h2o-demo-rfi" "rfi-assistant" "RFI-assistant";
update "ai.h2o.wave.study_partner" "study" "study-partner";
update "ai.h2o.wave.tomatoAI" "tomato-ai" "tomatoAI";
update "wave-h2ogpt-audio-summarization" "audio-summarization" "transcription-summarize";
update "ai.h2o.wave.weekly_meal_planning" "meal-planning" "weekly-dinner-plan";






