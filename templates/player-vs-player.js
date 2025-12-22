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
*/

// [1] Safe init
const selected = document.querySelector(".selected");
const optionsContainer = document.querySelector(".options-container");
const searchBox = document.querySelector(".search-box input");
const optionsList = document.querySelectorAll(".option");

if (selected && optionsContainer && searchBox) {               // [6]
  selected.addEventListener("click", () => {                   // [7]
    optionsContainer.classList.toggle("active");

    searchBox.value = "";
    filterList("");

    if (optionsContainer.classList.contains("active")) {
      searchBox.focus();
    }
  });

  optionsList.forEach(o => {
    o.addEventListener("click", () => {
      selected.textContent = o.querySelector("label").textContent;   // [23]
      optionsContainer.classList.remove("active");
    });
  });

  searchBox.addEventListener("keyup", function(e) {
    filterList(e.target.value);
  });
}


const filterList = searchTerm => {
  searchTerm = searchTerm.toLowerCase();
  optionsList.forEach(option => {
    // let label = option.firstElementChild.nextElementSibling.innerText.toLowerCase();
    let label = option.querySelector("label")?.innerText?.toLowerCase() || "";

    if (label.indexOf(searchTerm) != -1) {
      option.style.display = "block";
    } else {
      option.style.display = "none";
    }
  });
};


/*
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
*/

const selected1 = document.querySelector(".selected1");
const optionsContainer1 = document.querySelector(".options-container1");
const searchBox1 = document.querySelector(".search-box1 input");
const optionsList1 = document.querySelectorAll(".option1");

if (selected1 && optionsContainer1 && searchBox1) {                 // [55]
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
      selected1.textContent = o.querySelector("label").textContent; // [71]
      optionsContainer1.classList.remove("active");
    });
  });

  searchBox1.addEventListener("keyup", function(e) {
    filterList1(e.target.value);
  });
}


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

/*
var go = document.getElementById("go");
  if (go) {
    go.addEventListener("click", function (e) {
    var a=selected.innerHTML;
    var b=selected1.innerHTML;
    p=document.getElementById("t1");
    q=document.getElementById("t2");
    mt1p1=document.getElementById("mt1p1");
    mt1p2=document.getElementById("mt1p2");
    mt2p1=document.getElementById("mt2p1");
    mt2p2=document.getElementById("mt2p2");
    document.getElementById('m1').style.display='block'
    document.getElementById('m2').style.display='block'
    document.getElementById('d1').style.display='block'
    document.getElementById('d2').style.display='block'
    document.getElementById('d3').style.display='block'
    document.getElementById('d4').style.display='block'
    document.getElementById('d5').style.display='block'
    document.getElementById('d6').style.display='block'
    document.getElementById('batting_img').style.display='block'
    document.getElementById('bowling_img').style.display='block'
    document.getElementById('fielding_img').style.display='block'
    document.getElementById('matchup1').style.display='block'
    document.getElementById('matchup2').style.display='block'
    if (a=='Select Player' || b=='Select Player'){
            document.getElementById('m1').style.display='none'
            document.getElementById('m2').style.display='none'
            document.getElementById('d1').style.display='none'
            document.getElementById('d2').style.display='none'
            document.getElementById('d3').style.display='none'
            document.getElementById('d4').style.display='none'
            document.getElementById('d5').style.display='none'
            document.getElementById('d6').style.display='none'
            document.getElementById('batting_img').style.display='none'
            document.getElementById('bowling_img').style.display='none'
            document.getElementById('fielding_img').style.display='none'
            document.getElementById('matchup1').style.display='none'
            document.getElementById('matchup2').style.display='none'
            alert('Please select both the Players');
            document.getElementById('info').style.display='none';
            p.src=''
            p.classList=[]
            q.src=''
            q.classList=[]
        }
    else if (a==b){
            document.getElementById('m1').style.display='none'
            document.getElementById('m2').style.display='none'
            document.getElementById('d1').style.display='none'
            document.getElementById('d2').style.display='none'
            document.getElementById('d3').style.display='none'
            document.getElementById('d4').style.display='none'
            document.getElementById('d5').style.display='none'
            document.getElementById('d6').style.display='none'
            document.getElementById('matchup1').style.display='none'
            document.getElementById('matchup2').style.display='none'
            document.getElementById('batting_img').style.display='none'
            document.getElementById('bowling_img').style.display='none'
            document.getElementById('fielding_img').style.display='none'
            alert('Please select two different Players');
            document.getElementById('info').style.display='none';
            p.src=''
            p.classList=[]
            q.src=''
            q.classList=[]
        }
    else{
            $.ajax({
            url: '/playervsplayer',
            type: 'POST',
            data: { player1: a,player2:b},
            success: function(response) {
                // Handle the response from Flask
                console.log('Response:', response);
                p.src=response['result1']
                p.classList=[]
                p.classList.add('img1')
                q.src=response['result2']
                q.classList=[]
                q.classList.add('img2')
                mt1p1.src=response['result1']
                mt1p1.classList=[]
                mt1p1.classList.add('mtimg1')
                mt1p2.src=response['result2']
                mt1p2.classList=[]
                mt1p2.classList.add('mtimg2')
                mt2p1.src=response['result2']
                mt2p1.classList=[]
                mt2p1.classList.add('mtimg1')
                mt2p2.src=response['result1']
                mt2p2.classList=[]
                mt2p2.classList.add('mtimg2')
                var d1l1a=document.getElementById('d1l1a')
                var d1l2a=document.getElementById('d1l2a')
                var d1l3a=document.getElementById('d1l3a')
                var d1l4a=document.getElementById('d1l4a')
                var d1l5a=document.getElementById('d1l5a')
                var d1l6a=document.getElementById('d1l6a')
                var d2l1a=document.getElementById('d2l1a')
                var d2l2a=document.getElementById('d2l2a')
                var d2l3a=document.getElementById('d2l3a')
                var d2l4a=document.getElementById('d2l4a')
                var d2l5a=document.getElementById('d2l5a')
                var d2l6a=document.getElementById('d2l6a')
                var d3l1a=document.getElementById('d3l1a')
                var d3l2a=document.getElementById('d3l2a')
                var d3l3a=document.getElementById('d3l3a')
                var d3l4a=document.getElementById('d3l4a')
                var d4l1a=document.getElementById('d4l1a')
                var d4l2a=document.getElementById('d4l2a')
                var d4l3a=document.getElementById('d4l3a')
                var d4l4a=document.getElementById('d4l4a')
                var d4l5a=document.getElementById('d4l5a')
                var d4l6a=document.getElementById('d4l6a')
                var d5l1a=document.getElementById('d5l1a')
                var d5l2a=document.getElementById('d5l2a')
                var d5l3a=document.getElementById('d5l3a')
                var d5l4a=document.getElementById('d5l4a')
                var d5l5a=document.getElementById('d5l5a')
                var d5l6a=document.getElementById('d5l6a')
                var d6l1a=document.getElementById('d6l1a')
                var d6l2a=document.getElementById('d6l2a')
                var d6l3a=document.getElementById('d6l3a')
                var d6l4a=document.getElementById('d6l4a')
                var m1l1a=document.getElementById('m1l1a')
                var m1l2a=document.getElementById('m1l2a')
                var m1l3a=document.getElementById('m1l3a')
                var m1l4a=document.getElementById('m1l4a')
                var m1l5a=document.getElementById('m1l5a')
                var m1l6a=document.getElementById('m1l6a')
                var m1l7a=document.getElementById('m1l7a')
                var m2l1a=document.getElementById('m2l1a')
                var m2l2a=document.getElementById('m2l2a')
                var m2l3a=document.getElementById('m2l3a')
                var m2l4a=document.getElementById('m2l4a')
                var m2l5a=document.getElementById('m2l5a')
                var m2l6a=document.getElementById('m2l6a')
                var m2l7a=document.getElementById('m2l7a')
                d1l1a.innerHTML=response['mat_played1']
                d1l2a.innerHTML=response['runs1']
                d1l3a.innerHTML=response['avg1']
                d1l4a.innerHTML=response['sr1']
                d1l5a.innerHTML=response['fours1']
                d1l6a.innerHTML=response['sixes1']
                d2l1a.innerHTML=response['mat_played1']
                d2l2a.innerHTML=response['overs1']
                d2l3a.innerHTML=response['wickets1']
                d2l4a.innerHTML=response['economy1']
                d2l5a.innerHTML=response['srt1']
                d2l6a.innerHTML=response['wicket31']
                d3l1a.innerHTML=response['mat_played1']
                d3l2a.innerHTML=response['runout1']
                d3l3a.innerHTML=response['stumped1']
                d3l4a.innerHTML=response['catch1']
                d4l1a.innerHTML=response['mat_played2']
                d4l2a.innerHTML=response['runs2']
                d4l3a.innerHTML=response['avg2']
                d4l4a.innerHTML=response['sr2']
                d4l5a.innerHTML=response['fours2']
                d4l6a.innerHTML=response['sixes2']
                d5l1a.innerHTML=response['mat_played2']
                d5l2a.innerHTML=response['overs2']
                d5l3a.innerHTML=response['wickets2']
                d5l4a.innerHTML=response['economy2']
                d5l5a.innerHTML=response['srt2']
                d5l6a.innerHTML=response['wicket32']
                d6l1a.innerHTML=response['mat_played2']
                d6l2a.innerHTML=response['runout2']
                d6l3a.innerHTML=response['stumped2']
                d6l4a.innerHTML=response['catch2']
                m1l1a.innerHTML=response['runs_m1']
                m1l2a.innerHTML=response['balls_m1']
                m1l3a.innerHTML=response['sr_m1']
                m1l4a.innerHTML=response['avg_m1']
                m1l5a.innerHTML=response['dismissed_m1']
                m1l6a.innerHTML=response['economy_m1']
                m1l7a.innerHTML=response['balls_per_boundary_m1']
                m2l1a.innerHTML=response['runs_m2']
                m2l2a.innerHTML=response['balls_m2']
                m2l3a.innerHTML=response['sr_m2']
                m2l4a.innerHTML=response['avg_m2']
                m2l5a.innerHTML=response['dismissed_m2']
                m2l6a.innerHTML=response['economy_m2']
                m2l7a.innerHTML=response['balls_per_boundary_m2']
            },

        });
        }

      })
      }
*/



var go = document.getElementById("go");
if (go) {
  go.addEventListener("click", function () {

    const a = selected?.textContent?.trim() || "Select Player";      // [99]
    const b = selected1?.textContent?.trim() || "Select Player";

    // Don't show boxes until we validate
    const showAll = (show) => {                                      // [103]
      const ids = ['m1','m2','d1','d2','d3','d4','d5','d6','batting_img','bowling_img','fielding_img','matchup1','matchup2'];
      ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.style.display = show ? 'block' : 'none';
      });
    };

    showAll(false);                                                  // [111]

    if (a === 'Select Player' || b === 'Select Player') {
      alert('Please select both the Players');
      return;
    }
    if (a === b) {
      alert('Please select two different Players');
      return;
    }

    // Now show boxes (we have valid players)
    showAll(true);                                                   // [123]

    // Ensure jQuery exists before using it
    if (typeof window.$ === "undefined") {                           // [126]
      alert("jQuery not loaded. Load jQuery BEFORE player-vs-player.js");
      showAll(false);
      return;
    }

    $.ajax({
      url: '/playervsplayer',
      type: 'POST',
      dataType: 'json',                                              // [135] IMPORTANT
      data: { player1: a, player2: b },

      success: function(response) {

        // Defensive: if backend returned string, parse
        if (typeof response === "string") {                          // [142]
          try { response = JSON.parse(response); } catch(e) {}
        }

        // Images
        const p = document.getElementById("t1");
        const q = document.getElementById("t2");
        const mt1p1 = document.getElementById("mt1p1");
        const mt1p2 = document.getElementById("mt1p2");
        const mt2p1 = document.getElementById("mt2p1");
        const mt2p2 = document.getElementById("mt2p2");

        if (p) { p.src = response.result1 || ""; p.className = "img1"; }
        if (q) { q.src = response.result2 || ""; q.className = "img2"; }
        if (mt1p1) { mt1p1.src = response.result1 || ""; mt1p1.className = "mtimg1"; }
        if (mt1p2) { mt1p2.src = response.result2 || ""; mt1p2.className = "mtimg2"; }
        if (mt2p1) { mt2p1.src = response.result2 || ""; mt2p1.className = "mtimg1"; }
        if (mt2p2) { mt2p2.src = response.result1 || ""; mt2p2.className = "mtimg2"; }

        // Helper to set text safely
        const setText = (id, value) => {                             // [170]
          const el = document.getElementById(id);
          if (el) el.textContent = (value ?? "").toString();
        };

        // Player 1 batting
        setText('d1l1a', response.mat_played1);
        setText('d1l2a', response.runs1);
        setText('d1l3a', response.avg1);
        setText('d1l4a', response.sr1);
        setText('d1l5a', response.fours1);
        setText('d1l6a', response.sixes1);

        // Player 1 bowling
        setText('d2l1a', response.mat_played1);
        setText('d2l2a', response.overs1);
        setText('d2l3a', response.wickets1);
        setText('d2l4a', response.economy1);
        setText('d2l5a', response.srt1);
        setText('d2l6a', response.wicket31);

        // Player 1 fielding
        setText('d3l1a', response.mat_played1);
        setText('d3l2a', response.runout1);
        setText('d3l3a', response.stumped1);
        setText('d3l4a', response.catch1);

        // Player 2 batting
        setText('d4l1a', response.mat_played2);
        setText('d4l2a', response.runs2);
        setText('d4l3a', response.avg2);
        setText('d4l4a', response.sr2);
        setText('d4l5a', response.fours2);
        setText('d4l6a', response.sixes2);

        // Player 2 bowling
        setText('d5l1a', response.mat_played2);
        setText('d5l2a', response.overs2);
        setText('d5l3a', response.wickets2);
        setText('d5l4a', response.economy2);
        setText('d5l5a', response.srt2);
        setText('d5l6a', response.wicket32);

        // Player 2 fielding
        setText('d6l1a', response.mat_played2);
        setText('d6l2a', response.runout2);
        setText('d6l3a', response.stumped2);
        setText('d6l4a', response.catch2);

        // Matchup 1
        setText('m1l1a', response.runs_m1);
        setText('m1l2a', response.balls_m1);
        setText('m1l3a', response.sr_m1);
        setText('m1l4a', response.avg_m1);
        setText('m1l5a', response.dismissed_m1);
        setText('m1l6a', response.economy_m1);
        setText('m1l7a', response.balls_per_boundary_m1);

        // Matchup 2
        setText('m2l1a', response.runs_m2);
        setText('m2l2a', response.balls_m2);
        setText('m2l3a', response.sr_m2);
        setText('m2l4a', response.avg_m2);
        setText('m2l5a', response.dismissed_m2);
        setText('m2l6a', response.economy_m2);
        setText('m2l7a', response.balls_per_boundary_m2);
      },

      error: function(xhr, status, err) {                             // [256]
        console.error("AJAX error:", status, err, xhr.responseText);
        alert("Could not load stats. Check Flask /playervsplayer route.");
        showAll(false);
      }
    });

  });
}

