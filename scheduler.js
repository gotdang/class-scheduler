(function () {

  const classNamesFile = document.querySelector("#class-names-file"); // display: none
  const classNamesList = document.querySelector("#class-names-list");
  const classNamesImportButton = document.querySelector("#class-names-import-button");
  const startDateInput = document.querySelector("#start-date");

  function redirectImportButton(e) {
    let e2 = new MouseEvent("click", e);
    e2.target = classNamesFile;
    classNamesFile.dispatchEvent(e2);
    alert("MELN");
  }
  // function typingClassName(e) {
  //   // special cases for CJKT keyboards.
  //   if (e.isComposing || e.keyCode === 229) {
  //     return;
  //   }
  //   const keycode = (e.keyCode ? e.keyCode : e.which)
  //   if (keycode === 13) {
  //     xferClassName(e);
  //   }
  // }

  // Adds the specified class name to the list.
  // If the specified name starts with "<", the remainder of the name is prepended.
  // If the specified name starts with "-", the first (if any) occurrence of it in the list is removed.
  // If the specified name starts with ">", the remainder of the name is appended.
  // If the specified name doesn't start with any of those, it's appended.
  function addNameToList(className) {
    if (className.length > 0) {
      if (className.charAt(0) == "<") {
        // insert item at front of list
        className = className.substring(1);
        classNamesList.value = `${className}\n` + classNamesList.innerText;
      } else if (className.charAt(0) == "-") {
        // delete item from list
        className = className.substring(1) + "\n";
        let cl = classNamesList.value;
        let ci = cl.indexOf(className);
        if (ci >= 0) {
          let newList = cl.slice(0, ci) + cl.slice(ci + className.length);
          classNamesList.value = newList;
        }
      } else {
        // append item to list
        if (className.charAt(0) == ">") {
          // remove optional prefix
          className = className.substring(1);
        }
        classNamesList.value += `${className}\n`;
      }
    }
  }

  function updateStartDateWeekday() {
    const dayNames = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    let startDay = startDateInput.value.trim();
    try {
      startDay = dayNames[new Date(startDay).getDay()] || "";
    } catch (e) {
      startDay = "";
    }
    document.querySelector("#start-date-weekday").innerText = startDay && `(${startDay})`;
  }

  function uploadClassNameFile(evt) {
    const files = evt.target.files; // FileList object
    // use the 1st file from the list
    const f = files[0];
    const reader = new FileReader();

    // Closure to capture the file information.
    reader.onload = (function (theFile) {
      return function (e) {
        let nameList = e.target.result;
        // we have no idea what's in the file they select, so if there's an exception, bail...
        try {
          // divide it into lines
          nameList = nameList.split(new RegExp(/[\r\n]+/));
          // remove leading and trailing whitespace
          nameList = nameList.map(l => l.trim());
          // remove comment, section and empty/blank lines
          nameList = nameList.filter(l => l.length && ";[".indexOf(l.charAt(0)) < 0);
        } catch (e) {
          alert("There was a problem importing the file.");
          return undefined;
        }
        let currentList = classNamesList.value;
        // remove leading and trailing whitespace
        currentList = currentList.replace(/^\s*(.+)/, "$1").replace(/(.+\S)\s*$/, "$1");
        if (currentList.length) {
          currentList += "\n";
        }
        classNamesList.value = currentList + nameList.join("\n") + "\n";
        classNamesList.focus();
        classNamesList.scrollTop = classNamesList.scrollHeight;
        // clear the file input so the user can import the file more than once.
        evt.target.value = "";
        return nameList;
      };
    })(f);

    // Read in the image file as a data URL.
    reader.readAsText(f);
  }

  function init() {
    const DEFAULT_CHECKED = ["#tuesday-class", "#thursday-class", "#output-ical"];
    const DEFAULT_START_TIME = "18:30";
    const DEFAULT_DURATION = "3.5";

    for (let weekDay of DEFAULT_CHECKED) {
      document.querySelector(weekDay).checked = true;
    }
    document.querySelector("#session-time").value = DEFAULT_START_TIME;
    document.querySelector("#class-duration").value = DEFAULT_DURATION;

    classNamesFile.addEventListener("change", uploadClassNameFile, false);
    // The Import button redirects to the hidden file input button.
    classNamesImportButton.addEventListener("click", redirectImportButton);
    startDateInput.addEventListener("change", updateStartDateWeekday);
  }

  // Initialize this puppy when the window has finished loading.
  init();

})();