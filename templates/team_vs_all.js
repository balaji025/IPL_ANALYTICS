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
    $.ajax({
        url: '/teamvsalllabel',
        type: 'POST',
        data: { team: a},
        success: function(response) {
            // Handle the response from Flask
            console.log('Response:', response);
            document.getElementById("r1l1a").innerHTML=response['l1']
            document.getElementById("r1l2a").innerHTML=response['l2']
            document.getElementById("r1l3a").innerHTML=response['l3']
            document.getElementById("r1l4a").innerHTML=response['l4']
            document.getElementById("r1l5a").innerHTML=response['l5']
            document.getElementById("r2l1a").innerHTML=response['l6']
            document.getElementById("r2l2a").innerHTML=response['l7']
            document.getElementById("r2l3a").innerHTML=response['l8']
            document.getElementById("r2l4a").innerHTML=response['l9']
            document.getElementById("r2l5a").innerHTML=response['l10']
            document.getElementById("r3l1a").innerHTML=response['l11']
            document.getElementById("r3l2a").innerHTML=response['l12']
            document.getElementById("r3l3a").innerHTML=response['l13']
            document.getElementById("r3l4a").innerHTML=response['l14']
            document.getElementById("r3l5a").innerHTML=response['l15']
            document.getElementById("r4l1a").innerHTML=response['l16']
            document.getElementById("r4l2a").innerHTML=response['l17']
            document.getElementById("r4l3a").innerHTML=response['l18']
            document.getElementById("r4l4a").innerHTML=response['l19']
            document.getElementById("r4l5a").innerHTML=response['l20']
            document.getElementById("r5l1a").innerHTML=response['l21']
            document.getElementById("r5l2a").innerHTML=response['l22']
            document.getElementById("r5l3a").innerHTML=response['l23']
            document.getElementById("r5l4a").innerHTML=response['l24']
            document.getElementById("r5l5a").innerHTML=response['l25']
            document.getElementById("r6l1a").innerHTML=response['l26']
            document.getElementById("r6l2a").innerHTML=response['l27']
            document.getElementById("r6l3a").innerHTML=response['l28']
            document.getElementById("r6l4a").innerHTML=response['l29']
            document.getElementById("r6l5a").innerHTML=response['l30']
            document.getElementById("r7l1a").innerHTML=response['l31']
            document.getElementById("r7l2a").innerHTML=response['l32']
            document.getElementById("r7l3a").innerHTML=response['l33']
            document.getElementById("r7l4a").innerHTML=response['l34']
            document.getElementById("r7l5a").innerHTML=response['l35']
            document.getElementById("r8l1a").innerHTML=response['l36']
            document.getElementById("r8l2a").innerHTML=response['l37']
            document.getElementById("r8l3a").innerHTML=response['l38']
            document.getElementById("r8l4a").innerHTML=response['l39']
            document.getElementById("r8l5a").innerHTML=response['l40']
            document.getElementById("r9l1a").innerHTML=response['l41']
            document.getElementById("r9l2a").innerHTML=response['l42']
            document.getElementById("r9l3a").innerHTML=response['l43']
            document.getElementById("r9l4a").innerHTML=response['l44']
            document.getElementById("r9l5a").innerHTML=response['l45']
        }
    })
    var t1=document.getElementById("t1");
    // t1.src=`http://127.0.0.1:5000/static/images/ipl_tlogo/${a}.svg`
    t1.src = `/static/images/ipl_tlogo/${encodeURIComponent(a)}.svg`;

    t1.classList=[];
    document.getElementById("r1").style.display='block';
    document.getElementById("r2").style.display='block';
    document.getElementById("r3").style.display='block';
    document.getElementById("r4").style.display='block';
    document.getElementById("r5").style.display='block';
    document.getElementById("r6").style.display='block';
    document.getElementById("r7").style.display='block';
    document.getElementById("r8").style.display='block';
    document.getElementById("r9").style.display='block';
    document.getElementById("wl").style.display='block';

    //document.getElementById("s1").src=`http://127.0.0.1:5000/static/images/ipl_tvalogo/Chennai Super Kings.svg`;
    document.getElementById("s1").src = `/static/images/ipl_tvalogo/Chennai Super Kings.svg`;

    //document.getElementById("s2").src=`http://127.0.0.1:5000/static/images/ipl_tvalogo/Delhi Capitals.svg`;
    document.getElementById("s2").src = `/static/images/ipl_tvalogo/Delhi Capitals.svg`;

    // document.getElementById("s3").src=`http://127.0.0.1:5000/static/images/ipl_tvalogo/Gujarat Titans.svg`;
    document.getElementById("s3").src = `/static/images/ipl_tvalogo/Gujarat Titans.svg`;

    //document.getElementById("s4").src=`http://127.0.0.1:5000/static/images/ipl_tvalogo/Kolkata Knight Riders.svg`;
    document.getElementById("s4").src = `/static/images/ipl_tvalogo/Kolkata Knight Riders.svg`;

    //document.getElementById("s5").src=`http://127.0.0.1:5000/static/images/ipl_tvalogo/Lucknow Super Giants.svg`;
    document.getElementById("s5").src = `/static/images/ipl_tvalogo/Lucknow Super Giants.svg`;

    //document.getElementById("s6").src=`http://127.0.0.1:5000/static/images/ipl_tvalogo/Mumbai Indians.svg`;
    document.getElementById("s6").src = `/static/images/ipl_tvalogo/Mumbai Indians.svg`;

    //document.getElementById("s7").src=`http://127.0.0.1:5000/static/images/ipl_tvalogo/Punjab Kings.svg`;
    document.getElementById("s7").src = `/static/images/ipl_tvalogo/Punjab Kings.svg`;

    //document.getElementById("s8").src=`http://127.0.0.1:5000/static/images/ipl_tvalogo/Royal Challengers Bangalore.svg`;
    document.getElementById("s8").src = `/static/images/ipl_tvalogo/Royal Challengers Bangalore.svg`;

    //document.getElementById("s9").src=`http://127.0.0.1:5000/static/images/ipl_tvalogo/Rajasthan Royals.svg`;
    document.getElementById("s9").src = `/static/images/ipl_tvalogo/Rajasthan Royals.svg`;

    if (a=='Select Team'){
        alert('Select a Team')
        document.getElementById("r1").style.display='none';
        document.getElementById("r2").style.display='none';
        document.getElementById("r3").style.display='none';
        document.getElementById("r4").style.display='none';
        document.getElementById("r5").style.display='none';
        document.getElementById("r6").style.display='none';
        document.getElementById("r7").style.display='none';
        document.getElementById("r8").style.display='none';
        document.getElementById("r9").style.display='none';
        document.getElementById("wl").style.display='none';
        document.getElementById("s1").src='';
        document.getElementById("s2").src='';
        document.getElementById("s3").src='';
        document.getElementById("s4").src='';
        document.getElementById("s5").src='';
        document.getElementById("s6").src='';
        document.getElementById("s7").src='';
        document.getElementById("s8").src='';
        document.getElementById("s9").src='';
    }

    if (a=='Chennai Super Kings'){
        t1.classList.add('csk-1-icon');
        s=document.getElementById("s1");
        s.className="csk-s1-icon-srh"
        s.src=`/static/images/img/Sunrisers Hyderabad.svg`;
        document.getElementById("s2").className="dc-s1-icon";
        document.getElementById("s3").className="gt-s1-icon";
        document.getElementById("s4").className="kkr-s1-icon";
        document.getElementById("s5").className="lsg-s1-icon";
        document.getElementById("s6").className="mi-s1-icon";
        document.getElementById("s7").className="pbks-s1-icon";
        document.getElementById("s8").className="rcb-s1-icon";
        document.getElementById("s9").className="rr-s1-icon";
        }

    else if (a=='Gujarat Titans'){
        t1.classList.add('gt-1-icon')
        s=document.getElementById("s3")
        s.className="gt-s1-icon-srh"
        s.src=`/static/images/img/Sunrisers Hyderabad.svg`;
        document.getElementById("s1").className="csk-s1-icon";
        document.getElementById("s2").className="dc-s1-icon";
        document.getElementById("s4").className="kkr-s1-icon";
        document.getElementById("s5").className="lsg-s1-icon";
        document.getElementById("s6").className="mi-s1-icon";
        document.getElementById("s7").className="pbks-s1-icon";
        document.getElementById("s8").className="rcb-s1-icon";
        document.getElementById("s9").className="rr-s1-icon";
    }
    else if (a=='Delhi Capitals'){
        t1.classList.add('dc-1-icon')
        s=document.getElementById("s2")
        s.src=`/static/images/img/Sunrisers Hyderabad.svg`;
        document.getElementById("s1").className="csk-s1-icon";
        document.getElementById("s3").className="gt-s1-icon";
        document.getElementById("s4").className="kkr-s1-icon";
        document.getElementById("s5").className="lsg-s1-icon";
        document.getElementById("s6").className="mi-s1-icon";
        document.getElementById("s7").className="pbks-s1-icon";
        document.getElementById("s8").className="rcb-s1-icon";
        document.getElementById("s9").className="rr-s1-icon";
    }
    else if (a=='Rajasthan Royals'){
        t1.classList.add('rr-1-icon')
        s=document.getElementById("s9")
        s.className="rr-s1-icon-srh"
        s.src=`/static/images/img/Sunrisers Hyderabad.svg`;
        document.getElementById("s2").className="dc-s1-icon";
        document.getElementById("s3").className="gt-s1-icon";
        document.getElementById("s4").className="kkr-s1-icon";
        document.getElementById("s5").className="lsg-s1-icon";
        document.getElementById("s6").className="mi-s1-icon";
        document.getElementById("s7").className="pbks-s1-icon";
        document.getElementById("s8").className="rcb-s1-icon";
        document.getElementById("s1").className="csk-s1-icon";

    }
    else if (a=='Sunrisers Hyderabad'){
        t1.classList.add('srh-1-icon')
        document.getElementById("s1").className="csk-s1-icon";
        document.getElementById("s2").className="dc-s1-icon";
        document.getElementById("s3").className="gt-s1-icon";
        document.getElementById("s4").className="kkr-s1-icon";
        document.getElementById("s5").className="lsg-s1-icon";
        document.getElementById("s6").className="mi-s1-icon";
        document.getElementById("s7").className="pbks-s1-icon";
        document.getElementById("s8").className="rcb-s1-icon";
        document.getElementById("s9").className="rr-s1-icon";
    }
    else if (a=='Mumbai Indians'){
        t1.classList.add('mi-1-icon')
        s=document.getElementById("s6")
        s.className="mi-s1-icon-srh"
        s.src=`/static/images/img/Sunrisers Hyderabad.svg`;
        document.getElementById("s2").className="dc-s1-icon";
        document.getElementById("s3").className="gt-s1-icon";
        document.getElementById("s4").className="kkr-s1-icon";
        document.getElementById("s5").className="lsg-s1-icon";
        document.getElementById("s1").className="csk-s1-icon";
        document.getElementById("s7").className="pbks-s1-icon";
        document.getElementById("s8").className="rcb-s1-icon";
        document.getElementById("s9").className="rr-s1-icon";
    }
    else if (a=='Lucknow Super Giants'){
        t1.classList.add('lsg-1-icon')
        s=document.getElementById("s5")
        s.className="lsg-s1-icon-srh"
        s.src=`/static/images/img/Sunrisers Hyderabad.svg`;
        document.getElementById("s2").className="dc-s1-icon";
        document.getElementById("s3").className="gt-s1-icon";
        document.getElementById("s4").className="kkr-s1-icon";
        document.getElementById("s1").className="csk-s1-icon";
        document.getElementById("s6").className="mi-s1-icon";
        document.getElementById("s7").className="pbks-s1-icon";
        document.getElementById("s8").className="rcb-s1-icon";
        document.getElementById("s9").className="rr-s1-icon";
    }
    else if (a=='Royal Challengers Bangalore'){
        t1.classList.add('rcb-1-icon')
        s=document.getElementById("s8")
        s.className="rcb-s1-icon-srh"
        s.src=`/static/images/img/Sunrisers Hyderabad.svg`;
        document.getElementById("s2").className="dc-s1-icon";
        document.getElementById("s3").className="gt-s1-icon";
        document.getElementById("s4").className="kkr-s1-icon";
        document.getElementById("s5").className="lsg-s1-icon";
        document.getElementById("s6").className="mi-s1-icon";
        document.getElementById("s7").className="pbks-s1-icon";
        document.getElementById("s1").className="csk-s1-icon";
        document.getElementById("s9").className="rr-s1-icon";

    }
    else if (a=='Punjab Kings'){
        t1.classList.add('pbks-1-icon')
        s=document.getElementById("s7")
        s.className="pbks-s1-icon-srh"
        s.src=`/static/images/img/Sunrisers Hyderabad.svg`;
        document.getElementById("s2").className="dc-s1-icon";
        document.getElementById("s3").className="gt-s1-icon";
        document.getElementById("s4").className="kkr-s1-icon";
        document.getElementById("s5").className="lsg-s1-icon";
        document.getElementById("s6").className="mi-s1-icon";
        document.getElementById("s1").className="csk-s1-icon";
        document.getElementById("s8").className="rcb-s1-icon";
        document.getElementById("s9").className="rr-s1-icon";
    }
    else if (a=='Kolkata Knight Riders'){
        t1.classList.add('kkr-1-icon')
        s=document.getElementById("s4")
        s.className="kkr-s1-icon-srh"
        s.src=`/static/images/img/Sunrisers Hyderabad.svg`;
        document.getElementById("s2").className="dc-s1-icon";
        document.getElementById("s3").className="gt-s1-icon";
        document.getElementById("s1").className="csk-s1-icon";
        document.getElementById("s5").className="lsg-s1-icon";
        document.getElementById("s6").className="mi-s1-icon";
        document.getElementById("s7").className="pbks-s1-icon";
        document.getElementById("s8").className="rcb-s1-icon";
        document.getElementById("s9").className="rr-s1-icon";
    }

     })
  }

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
  const selected = document.querySelector(".selected");
  const optionsContainer = document.querySelector(".options-container");
  const searchBox = document.querySelector(".search-box input");
  const optionsList = document.querySelectorAll(".option");

  // ---- Dropdown ----
  selected.addEventListener("click", () => {
    optionsContainer.classList.toggle("active");
    searchBox.value = "";
    filterList("");
    if (optionsContainer.classList.contains("active")) searchBox.focus();
  });

  optionsList.forEach(o => {
    o.addEventListener("click", () => {
      selected.textContent = o.querySelector("label")?.textContent?.trim() || "Select Team";
      optionsContainer.classList.remove("active");
    });
  });

  searchBox.addEventListener("keyup", (e) => filterList(e.target.value));

  function filterList(term) {
    const s = (term || "").toLowerCase();
    optionsList.forEach(option => {
      const label = option.querySelector("label")?.innerText?.toLowerCase() || "";
      option.style.display = label.includes(s) ? "block" : "none";
    });
  }

  // ---- Helpers ----
  const showBlocks = (show) => {
    const ids = ["r1","r2","r3","r4","r5","r6","r7","r8","r9","wl"];
    ids.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.style.display = show ? "block" : "none";
    });
  };

  const clearSmallLogos = () => {
    for (let i = 1; i <= 9; i++) {
      const el = document.getElementById(`s${i}`);
      if (el) el.src = "";
    }
  };

  const setAllSmallLogosDefault = () => {
    const map = {
      s1: "Chennai Super Kings",
      s2: "Delhi Capitals",
      s3: "Gujarat Titans",
      s4: "Kolkata Knight Riders",
      s5: "Lucknow Super Giants",
      s6: "Mumbai Indians",
      s7: "Punjab Kings",
      s8: "Royal Challengers Bangalore",
      s9: "Rajasthan Royals",
    };
    Object.entries(map).forEach(([id, team]) => {
      const el = document.getElementById(id);
      if (el) el.src = `/static/images/ipl_tvalogo/${encodeURIComponent(team)}.svg`;
    });
  };

  const replaceOneLogoWithSRH = (logoId, srhClassName) => {
    const el = document.getElementById(logoId);
    if (!el) return;
    el.className = srhClassName; // swap positioning class
    el.src = `/static/images/img/Sunrisers Hyderabad.svg`;
  };

  const resetSmallLogoClasses = () => {
    // restore base classes (your CSS defaults)
    const base = {
      s1: "csk-s1-icon",
      s2: "dc-s1-icon",
      s3: "gt-s1-icon",
      s4: "kkr-s1-icon",
      s5: "lsg-s1-icon",
      s6: "mi-s1-icon",
      s7: "pbks-s1-icon",
      s8: "rcb-s1-icon",
      s9: "rr-s1-icon",
    };
    Object.entries(base).forEach(([id, cls]) => {
      const el = document.getElementById(id);
      if (el) el.className = cls;
    });
  };

  // ---- GO button ----
  const go = document.getElementById("go");
  go.addEventListener("click", () => {
    const a = selected.textContent.trim();

    const t1 = document.getElementById("t1");

    // guard
    if (a === "Select Team") {
      alert("Select a Team");
      showBlocks(false);
      if (t1) { t1.src = ""; t1.className = "bb"; }
      clearSmallLogos();
      return;
    }

    // must have jQuery (because you're using $.ajax)
    if (typeof window.$ === "undefined") {
      alert("jQuery not loaded. Load it BEFORE team_vs_all.js");
      return;
    }

    // show layout blocks FIRST so it feels responsive
    showBlocks(true);

    // main logo
    if (t1) {
      t1.src = `/static/images/ipl_tlogo/${encodeURIComponent(a)}.svg`;
      t1.className = ""; // clear properly
    }

    // choose big team class
    const bigClass = {
      "Chennai Super Kings": "csk-1-icon",
      "Delhi Capitals": "dc-1-icon",
      "Gujarat Titans": "gt-1-icon",
      "Kolkata Knight Riders": "kkr-1-icon",
      "Lucknow Super Giants": "lsg-1-icon",
      "Mumbai Indians": "mi-1-icon",
      "Punjab Kings": "pbks-1-icon",
      "Rajasthan Royals": "rr-1-icon",
      "Royal Challengers Bangalore": "rcb-1-icon",
      "Sunrisers Hyderabad": "srh-1-icon",
    };
    if (t1) t1.classList.add(bigClass[a] || "rcb-1-icon");

    // small logos
    resetSmallLogoClasses();
    setAllSmallLogosDefault();

    // Replace the selected team’s small logo with SRH
    const replaceMap = {
      "Chennai Super Kings": ["s1", "csk-s1-icon-srh"],
      "Delhi Capitals": ["s2", "dc-s1-icon"],          // you never defined dc-s1-icon-srh; keeping original class
      "Gujarat Titans": ["s3", "gt-s1-icon-srh"],
      "Kolkata Knight Riders": ["s4", "kkr-s1-icon-srh"],
      "Lucknow Super Giants": ["s5", "lsg-s1-icon-srh"],
      "Mumbai Indians": ["s6", "mi-s1-icon-srh"],
      "Punjab Kings": ["s7", "pbks-s1-icon-srh"],
      "Royal Challengers Bangalore": ["s8", "rcb-s1-icon-srh"],
      "Rajasthan Royals": ["s9", "rr-s1-icon-srh"],
    };
    if (replaceMap[a]) {
      const [logoId, cls] = replaceMap[a];
      replaceOneLogoWithSRH(logoId, cls);
    }

    // ---- AJAX: stats ----
    $.ajax({
      url: "/teamvsalllabel",
      type: "POST",
      dataType: "json",
      data: { team: a },

      success: function (response) {
        console.log("Response:", response);

        // Fill 45 fields
        for (let i = 1; i <= 45; i++) {
          const elId = i <= 5 ? `r1l${i}a`
                    : i <= 10 ? `r2l${i - 5}a`
                    : i <= 15 ? `r3l${i - 10}a`
                    : i <= 20 ? `r4l${i - 15}a`
                    : i <= 25 ? `r5l${i - 20}a`
                    : i <= 30 ? `r6l${i - 25}a`
                    : i <= 35 ? `r7l${i - 30}a`
                    : i <= 40 ? `r8l${i - 35}a`
                    : `r9l${i - 40}a`;

          const el = document.getElementById(elId);
          if (el) el.textContent = (response[`l${i}`] ?? "").toString();
        }
      },

      error: function (xhr, status, err) {
        console.error("AJAX error:", status, err, xhr.responseText);
        alert("Stats request failed. Check /teamvsalllabel backend.");
        showBlocks(false);
      }
    });
  });
});
