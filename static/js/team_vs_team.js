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

const selected1 = document.querySelector(".selected1");
const optionsContainer1 = document.querySelector(".options-container1");
const searchBox1 = document.querySelector(".search-box1 input");

const optionsList1 = document.querySelectorAll(".option1");

selected1.addEventListener("click", () => {
  optionsContainer1.classList.toggle("active");

  searchBox1.value = "";
  filterList1("");

  if (optionsContainer1.classList.contains("active")) {
    searchBox1.focus();
  }
});

optionsList1.forEach(o => {
  o.addEventListener("click", () => {
    selected1.innerHTML = o.querySelector("label").innerHTML;
    optionsContainer1.classList.remove("active");
  });
});

searchBox1.addEventListener("keyup", function(e) {
  filterList1(e.target.value);
});

const filterList1 = searchTerm1 => {
  searchTerm1 = searchTerm1.toLowerCase();
  optionsList1.forEach(option => {
    let label = option.firstElementChild.nextElementSibling.innerText.toLowerCase();
    if (label.indexOf(searchTerm1) != -1) {
      option.style.display = "block";
    } else {
      option.style.display = "none";
    }
  });
};

var go = document.getElementById("go");
  if (go) {
    go.addEventListener("click", function (e) {
        var a=selected.innerHTML;
        var b=selected1.innerHTML;
        var t1=document.getElementById('t1')
        var t2=document.getElementById('t2')
        var inf=document.getElementById('info')
        inf.style.display='block';

        if (a=='Select Team' || b=='Select Team'){
            alert('Please select both the teams');
            document.getElementById('info').style.display='none';
            t1.src=''
            t1.classList=[]
            t2.src=''
            t2.classList=[]
        }
        else if (a==b){
            alert('Please select two different teams');
            document.getElementById('info').style.display='none';
            t1.src=''
            t1.classList=[]
            t2.src=''
            t2.classList=[]
        }
        else{
            // t1.src=`http://127.0.0.1:5000/static/images/ipl_tlogo/${a}.svg`

            t1.src = `/static/images/ipl_tlogo/${encodeURIComponent(a)}.svg`;


            t1.classList=[]
            if (a=='Chennai Super Kings'){
                t1.classList.add('csk-2-icon');
            }
            else if (a=='Delhi Capitals'){
                t1.classList.add('dc-2-icon');
            }
            else if (a=='Gujarat Titans'){
                t1.classList.add('gt-2-icon');
            }
            else if (a=='Kolkata Knight Riders'){
                t1.classList.add('kkr-2-icon');
            }
            else if (a=='Lucknow Super Giants'){
                t1.classList.add('lsg-2-icon');
            }
            else if (a=='Mumbai Indians'){
                t1.classList.add('mi-2r-icon');
            }
            else if (a=='Punjab Kings'){
                t1.classList.add('pbks-2r-icon');
            }
            else if (a=='Rajasthan Royals'){
                t1.classList.add('rr-2r-icon');
            }
            else if (a=='Royal Challengers Bangalore'){
                t1.classList.add('rcb-2r-icon');
            }
            else if (a=='Sunrisers Hyderabad'){
                t1.classList.add('srh-2r-icon');
            }

            // t2.src=`http://127.0.0.1:5000/static/images/ipl_tlogo/${b}.svg`

            t2.src = `/static/images/ipl_tlogo/${encodeURIComponent(b)}.svg`;

            t2.classList=[]
            if (b=='Chennai Super Kings'){
                t2.classList.add('csk-2r-icon');
            }
            else if (b=='Delhi Capitals'){
                t2.classList.add('dc-2r-icon');
            }
            else if (b=='Gujarat Titans'){
                t2.classList.add('gt-2r-icon');
            }
            else if (b=='Kolkata Knight Riders'){
                t2.classList.add('kkr-2r-icon');
            }
            else if (b=='Lucknow Super Giants'){
                t2.classList.add('lsg-2r-icon');
            }
            else if (b=='Mumbai Indians'){
                t2.classList.add('mi-2-icon');
            }
            else if (b=='Punjab Kings'){
                t2.classList.add('pbks-2-icon');
            }
            else if (b=='Rajasthan Royals'){
                t2.classList.add('rr-2-icon');
            }
            else if (b=='Royal Challengers Bangalore'){
                t2.classList.add('rcb-2-icon');
            }
            else if (b=='Sunrisers Hyderabad'){
                t2.classList.add('srh-2-icon');
            }
            $.ajax({
                url: '/teamvsteamlabel',
                type: 'POST',
                data: { team1:a, team2:b},
                success: function(response) {
                    // Handle the response from Flask
                    console.log('Response:', response);
                    var l1=document.getElementById("l1a")
                    var l2=document.getElementById("l2a")
                    var l3=document.getElementById("l3a")
                    var l4=document.getElementById("l4a")
                    var l5=document.getElementById("l5a")
                    var l6=document.getElementById("l6a")
                    var l71=document.getElementById("l71a")
                    var l72=document.getElementById("l72a")
                    var l81=document.getElementById("l81a")
                    var l82=document.getElementById("l82a")
                    var l91=document.getElementById("l91a")
                    var l92=document.getElementById("l92a")
                    if (response['d1']=='Batting'){
                        l91.style.left='65px';
                    }
                    if (response['d1']=='Bowling'){
                        l91.style.left='60px';
                    }
                    if (response['d1']=='Balanced'){
                        l91.style.left='55px';
                    }
                    if (response['d2']=='Batting'){
                        l92.style.left='475px';
                    }
                    if (response['d2']=='Bowling'){
                        l92.style.left='470px';
                    }
                    if (response['d2']=='Balanced'){
                        l92.style.left='465px';
                    }

                    var l101=document.getElementById("l101a")
                    var l102=document.getElementById("l102a")
                    var l111=document.getElementById("l111a")
                    var l112=document.getElementById("l112a")
                    var l121=document.getElementById("l121a")
                    var l122=document.getElementById("l122a")
                    l1.innerHTML = response['total_matches']
                    l2.innerHTML = response['t1won']
                    l3.innerHTML = response['t2won']
                    l4.innerHTML = response['no_result']
                    l5.innerHTML = response['t1winper']
                    l6.innerHTML = response['t2winper']
                    l71.innerHTML = response['msg1']
                    l72.innerHTML = response['msg2']
                    l81.innerHTML = response['m1']
                    l82.innerHTML = response['m2']
                    l81.innerHTML = response['m1']
                    l82.innerHTML = response['m2']
                    l91.innerHTML = response['d1']
                    l92.innerHTML = response['d2']
                    l101.innerHTML = response['nrr1']
                    l102.innerHTML = response['nrr2']
                    l111.innerHTML = response['or_cap1']
                    l112.innerHTML = response['or_cap2']
                    l121.innerHTML = response['pur_cap1']
                    l122.innerHTML = response['pur_cap2']

                    },
                });
}

    })
    }

*/


document.addEventListener("DOMContentLoaded", () => {

  // ---------- Dropdown 1 ----------
  const selected = document.querySelector(".selected");
  const optionsContainer = document.querySelector(".options-container");
  const searchBox = document.querySelector(".search-box input");
  const optionsList = document.querySelectorAll(".option");

  if (selected && optionsContainer && searchBox) {
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
  }

  // ---------- Dropdown 2 ----------
  const selected1 = document.querySelector(".selected1");
  const optionsContainer1 = document.querySelector(".options-container1");
  const searchBox1 = document.querySelector(".search-box1 input");
  const optionsList1 = document.querySelectorAll(".option1");

  if (selected1 && optionsContainer1 && searchBox1) {
    selected1.addEventListener("click", () => {
      optionsContainer1.classList.toggle("active");
      searchBox1.value = "";
      filterList1("");
      if (optionsContainer1.classList.contains("active")) searchBox1.focus();
    });

    optionsList1.forEach(o => {
      o.addEventListener("click", () => {
        selected1.textContent = o.querySelector("label")?.textContent?.trim() || "Select Team";
        optionsContainer1.classList.remove("active");
      });
    });

    searchBox1.addEventListener("keyup", (e) => filterList1(e.target.value));

    function filterList1(term) {
      const s = (term || "").toLowerCase();
      optionsList1.forEach(option => {
        const label = option.querySelector("label")?.innerText?.toLowerCase() || "";
        option.style.display = label.includes(s) ? "block" : "none";
      });
    }
  }

  // ---------- GO + AJAX ----------
  const go = document.getElementById("go");
  if (!go) return;

  go.addEventListener("click", () => {
    const a = selected?.textContent?.trim() || "Select Team";
    const b = selected1?.textContent?.trim() || "Select Team";

    const t1 = document.getElementById("t1");
    const t2 = document.getElementById("t2");
    const inf = document.getElementById("info");

    if (inf) inf.style.display = "block";

    const hideAll = () => {
      if (inf) inf.style.display = "none";
      if (t1) { t1.src = ""; t1.className = ""; }
      if (t2) { t2.src = ""; t2.className = ""; }
    };

    if (a === "Select Team" || b === "Select Team") {
      alert("Please select both the teams");
      hideAll();
      return;
    }
    if (a === b) {
      alert("Please select two different teams");
      hideAll();
      return;
    }

    // logos (with safe URL encoding)
    if (t1) {
      t1.src = `/static/images/ipl_tlogo/${encodeURIComponent(a)}.svg`;
      t1.className = ""; // clear classes reliably
      t1.classList.add(teamClassLeft(a));
    }
    if (t2) {
      t2.src = `/static/images/ipl_tlogo/${encodeURIComponent(b)}.svg`;
      t2.className = "";
      t2.classList.add(teamClassRight(b));
    }

    // jQuery check
    if (typeof window.$ === "undefined") {
      alert("jQuery not loaded. Load jQuery BEFORE team_vs_team.js");
      return;
    }

    $.ajax({
      url: "/teamvsteamlabel",
      type: "POST",
      dataType: "json",                 // ✅ IMPORTANT
      data: { team1: a, team2: b },

      success: function (response) {
        console.log("Response:", response);

        // Helper
        const setText = (id, val) => {
          const el = document.getElementById(id);
          if (el) el.textContent = (val ?? "").toString();
        };

        // Position tweaks for Dept Better In
        const l91 = document.getElementById("l91a");
        const l92 = document.getElementById("l92a");
        if (l91 && response.d1) {
          l91.style.left = response.d1 === "Batting" ? "65px"
                      : response.d1 === "Bowling" ? "60px"
                      : "55px";
        }
        if (l92 && response.d2) {
          l92.style.left = response.d2 === "Batting" ? "475px"
                      : response.d2 === "Bowling" ? "470px"
                      : "465px";
        }

        // Fill values (IDs from your HTML)
        setText("l1a", response.total_matches);
        setText("l2a", response.t1won);
        setText("l3a", response.t2won);
        setText("l4a", response.no_result);
        setText("l5a", response.t1winper);
        setText("l6a", response.t2winper);

        setText("l71a", response.msg1);
        setText("l72a", response.msg2);

        setText("l81a", response.m1);
        setText("l82a", response.m2);

        setText("l91a", response.d1);
        setText("l92a", response.d2);

        setText("l101a", response.nrr1);
        setText("l102a", response.nrr2);

        setText("l111a", response.or_cap1);
        setText("l112a", response.or_cap2);

        setText("l121a", response.pur_cap1);
        setText("l122a", response.pur_cap2);
      },

      error: function (xhr, status, err) {
        console.error("AJAX error:", status, err, xhr.responseText);
        alert("Stats request failed. Check /teamvsteamlabel backend.");
        // don't hide logos; just hide stats panel
        if (inf) inf.style.display = "none";
      }
    });
  });

  // Mapping functions (matches your existing CSS classes)
  function teamClassLeft(team) {
    // left side uses the "-2-icon" OR some of your "-2r-icon" (as you had)
    const map = {
      "Chennai Super Kings": "csk-2-icon",
      "Delhi Capitals": "dc-2-icon",
      "Gujarat Titans": "gt-2-icon",
      "Kolkata Knight Riders": "kkr-2-icon",
      "Lucknow Super Giants": "lsg-2-icon",
      "Mumbai Indians": "mi-2r-icon",
      "Punjab Kings": "pbks-2r-icon",
      "Rajasthan Royals": "rr-2r-icon",
      "Royal Challengers Bangalore": "rcb-2r-icon",
      "Sunrisers Hyderabad": "srh-2r-icon"
    };
    return map[team] || "aa";
  }

  function teamClassRight(team) {
    const map = {
      "Chennai Super Kings": "csk-2r-icon",
      "Delhi Capitals": "dc-2r-icon",
      "Gujarat Titans": "gt-2r-icon",
      "Kolkata Knight Riders": "kkr-2r-icon",
      "Lucknow Super Giants": "lsg-2r-icon",
      "Mumbai Indians": "mi-2-icon",
      "Punjab Kings": "pbks-2-icon",
      "Rajasthan Royals": "rr-2-icon",
      "Royal Challengers Bangalore": "rcb-2-icon",
      "Sunrisers Hyderabad": "srh-2-icon"
    };
    return map[team] || "bb";
  }

});
