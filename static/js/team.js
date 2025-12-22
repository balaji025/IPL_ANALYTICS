/*
const selected = document.querySelector(".selected");
const optionsContainer = document.querySelector(".options-container");
const searchBox = document.querySelector(".search-box input");

const optionsList = document.querySelectorAll(".option");

selected.addEventListener("click", () => {
  optionsContainer.classList.toggle("active");

  searchBox.value = "";
  filterList("");

  if (optionsContainer.classList.contains("active")) {
    searchBox.focus();
  }
});

optionsList.forEach(o => {
  o.addEventListener("click", () => {
    selected.innerHTML = o.querySelector("label").innerHTML;
    optionsContainer.classList.remove("active");
  });
});

var go = document.getElementById("go");
  if (go) {
    go.addEventListener("click", function (e) {
    var a=selected.innerHTML;
    var t1=document.getElementById("t1");

    const teamSlug = encodeURIComponent(a);


    //t1.src=`http://127.0.0.1:5000/static/images/ipl_tlogo/${a}.svg`
    t1.src=`/static/images/ipl_tlogo/${teamSlug}.svg`

    var t2=document.getElementById("t2");
    //t2.src=`http://127.0.0.1:5000/static/images/ipl_tlogo/${a}.svg`
    t2.src=`/static/images/ipl_tlogo/${teamSlug}.svg`

    t1.classList=[];
    t2.classList=[];
    var inf=document.getElementById('info')

    inf.style.display='block';
    if (a=='Select Team'){
        alert('Select a Team')
        document.getElementById('info').style.display='none';
    }


    var a = selected.textContent.trim();
    if (a === 'Select Team') {
        alert('Select a Team');
        document.getElementById('info').style.display = 'none';
        return;
    }
    document.getElementById('info').style.display = 'block';


    else if (a=='Chennai Super Kings'){
        t1.classList.add('csk-1-icon');
        t2.classList.add('csk-1-ficon');

    }
    else if (a=='Gujarat Titans'){
        t1.classList.add('gt-1-icon')
        t2.classList.add('gt-1-ficon')
    }
    else if (a=='Delhi Capitals'){
        t1.classList.add('dc-1-icon')
        t2.classList.add('dc-1-ficon')
    }
    else if (a=='Rajasthan Royals'){
        t1.classList.add('rr-1-icon')
        t2.classList.add('rr-1-ficon')
    }
    else if (a=='Sunrisers Hyderabad'){
        t1.classList.add('srh-1-icon')
        t2.classList.add('srh-1-ficon')
    }
    else if (a=='Mumbai Indians'){
        t1.classList.add('mi-1-icon')
        t2.classList.add('mi-1-ficon')
    }
    else if (a=='Lucknow Super Giants'){
        t1.classList.add('lsg-1-icon')
        t2.classList.add('lsg-1-ficon')
    }
    else if (a=='Royal Challengers Bangalore'){
        t1.classList.add('rcb-1-icon')
        t2.classList.add('rcb-1-ficon')
    }
    else if (a=='Punjab Kings'){
        t1.classList.add('pbks-1-icon')
        t2.classList.add('pbks-1-ficon')
    }
    else if (a=='Kolkata Knight Riders'){
        t1.classList.add('kkr-1-icon')
        t2.classList.add('kkr-1-ficon')
    }

        $.ajax({
        url: '/teamlabel',
        type: 'POST',
        data: { team: a},
        success: function(response) {
            // Handle the response from Flask
            console.log('Response:', response);
            var l1=document.getElementById("l1a")
            newText = response['trophies'].replace(/ /g, "&nbsp;");
            l1.innerHTML = newText;
            var l2=document.getElementById("l2a")
            var l3=document.getElementById("l3a")
            var l4=document.getElementById("l4a")
            var l5=document.getElementById("l5a")
            var l6=document.getElementById("l6a")
            var l7=document.getElementById("l7a")
            var l8=document.getElementById("l8a")
            var l9=document.getElementById("l9a")
            var l10=document.getElementById("l10a")
            var l11=document.getElementById("l11a")
            var l12=document.getElementById("l12a")
            var l13=document.getElementById("l13a")

            l2.innerHTML=response['played']
            l3.innerHTML=response['won']
            l4.innerHTML=response['lost']
            l5.innerHTML=response['nr']
            l6.innerHTML=response['top4']
            l7.innerHTML=response['max_score']
            l8.innerHTML=response['min_score']
            l9.innerHTML=response['hrs']
            l10.innerHTML=response['hwt']
            l11.innerHTML=response['or_cap'].replace(/ /g, "&nbsp;");
            l12.innerHTML=response['pr_cap'].replace(/ /g, "&nbsp;");
            l13.innerHTML=response['captain']
            },
        });
         })
      }


    $.ajax({
      url: '/teamlabel',
      type: 'POST',
      dataType: 'json',
      data: { team: a },

      success: function(response) {
        console.log('Response:', response);

        const setText = (id, v) => {
          const el = document.getElementById(id);
          if (el) el.textContent = (v ?? "").toString();
        };

        // trophies/orange/purple spacing: if you really want non-breaking spaces,
        // do it safely on textContent by just leaving normal spaces (CSS handles nowrap already)
        setText("l1a", response.trophies);
        setText("l2a", response.played);
        setText("l3a", response.won);
        setText("l4a", response.lost);
        setText("l5a", response.nr);
        setText("l6a", response.top4);
        setText("l7a", response.max_score);
        setText("l8a", response.min_score);
        setText("l9a", response.hrs);
        setText("l10a", response.hwt);
        setText("l11a", response.or_cap);
        setText("l12a", response.pr_cap);
        setText("l13a", response.captain);
      },

      error: function(xhr, status, err) {
        console.error("AJAX error:", status, err, xhr.responseText);
        alert("Could not load team stats. Check /teamlabel route.");
        document.getElementById('info').style.display = 'none';
      }
    });


searchBox.addEventListener("keyup", function(e) {
  filterList(e.target.value);
});
const filterList = searchTerm => {
  searchTerm = searchTerm.toLowerCase();
  optionsList.forEach(option => {
    let label = option.firstElementChild.nextElementSibling.innerText.toLowerCase();
    if (label.indexOf(searchTerm) != -1) {
      option.style.display = "block";
    } else {
      option.style.display = "none";
    }
  });
};
*/

document.addEventListener("DOMContentLoaded", () => {

  /* =========================
     DROPDOWN (SELECT TEAM)
     ========================= */

  const selected = document.getElementById("team");
  const optionsContainer = document.querySelector(".options-container");
  const searchBox = document.querySelector(".search-box input");
  const optionsList = document.querySelectorAll(".option");

  if (!selected || !optionsContainer || !searchBox) {
    console.error("Team dropdown elements not found");
    return;
  }

  selected.addEventListener("click", () => {
    optionsContainer.classList.toggle("active");
    searchBox.value = "";
    filterList("");
    if (optionsContainer.classList.contains("active")) {
      searchBox.focus();
    }
  });

  optionsList.forEach((option) => {
    option.addEventListener("click", () => {
      const label = option.querySelector("label");
      selected.textContent = label ? label.textContent.trim() : "Select Team";
      optionsContainer.classList.remove("active");
    });
  });

  searchBox.addEventListener("keyup", (e) => {
    filterList(e.target.value);
  });

  function filterList(term) {
    const search = (term || "").toLowerCase();
    optionsList.forEach((option) => {
      const label = option.querySelector("label")?.innerText.toLowerCase() || "";
      option.style.display = label.includes(search) ? "block" : "none";
    });
  }

  /* =========================
     GO BUTTON + TEAM LOGO
     ========================= */

  const go = document.getElementById("go");
  const t1 = document.getElementById("t1");
  const t2 = document.getElementById("t2");
  const info = document.getElementById("info");

  if (!go || !t1 || !t2 || !info) {
    console.error("GO button or image/info elements missing");
    return;
  }

  go.addEventListener("click", () => {
    const teamName = selected.textContent.trim();

    if (teamName === "Select Team") {
      alert("Select a Team");
      info.style.display = "none";
      return;
    }

    // Reset images
    t1.className = "";
    t2.className = "";

    // Encode team name for URL
    const teamSlug = encodeURIComponent(teamName);
    t1.src = `/static/images/ipl_tlogo/${teamSlug}.svg`;
    t2.src = `/static/images/ipl_tlogo/${teamSlug}.svg`;

    // Apply team-specific CSS classes
    const classMap = {
      "Chennai Super Kings": ["csk-1-icon", "csk-1-ficon"],
      "Gujarat Titans": ["gt-1-icon", "gt-1-ficon"],
      "Delhi Capitals": ["dc-1-icon", "dc-1-ficon"],
      "Rajasthan Royals": ["rr-1-icon", "rr-1-ficon"],
      "Sunrisers Hyderabad": ["srh-1-icon", "srh-1-ficon"],
      "Mumbai Indians": ["mi-1-icon", "mi-1-ficon"],
      "Lucknow Super Giants": ["lsg-1-icon", "lsg-1-ficon"],
      "Royal Challengers Bangalore": ["rcb-1-icon", "rcb-1-ficon"],
      "Punjab Kings": ["pbks-1-icon", "pbks-1-ficon"],
      "Kolkata Knight Riders": ["kkr-1-icon", "kkr-1-ficon"]
    };

    if (classMap[teamName]) {
      t1.classList.add(classMap[teamName][0]);
      t2.classList.add(classMap[teamName][1]);
    }

    info.style.display = "block";

    /* =========================
       AJAX – TEAM STATS
       ========================= */

    if (typeof window.$ === "undefined") {
      alert("jQuery not loaded. Load jQuery BEFORE team.js");
      info.style.display = "none";
      return;
    }

    $.ajax({
      url: "/teamlabel",
      type: "POST",
      dataType: "json",
      data: { team: teamName },

      success: function (response) {
        const setText = (id, val) => {
          const el = document.getElementById(id);
          if (el) el.textContent = val ?? "";
        };

        setText("l1a", response.trophies);
        setText("l2a", response.played);
        setText("l3a", response.won);
        setText("l4a", response.lost);
        setText("l5a", response.nr);
        setText("l6a", response.top4);
        setText("l7a", response.max_score);
        setText("l8a", response.min_score);
        setText("l9a", response.hrs);
        setText("l10a", response.hwt);
        setText("l11a", response.or_cap);
        setText("l12a", response.pr_cap);
        setText("l13a", response.captain);
      },

      error: function (xhr, status, err) {
        console.error("AJAX error:", status, err, xhr.responseText);
        alert("Failed to load team stats.");
        info.style.display = "none";
      }
    });
  });

});
