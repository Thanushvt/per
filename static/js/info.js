document.addEventListener("DOMContentLoaded", function () {
    function validateCheckboxes(name) {
        const checkboxes = document.querySelectorAll(`input[name="${name}"]`);
        checkboxes.forEach((checkbox) => {
            checkbox.addEventListener("change", function () {
                let checkedBoxes = Array.from(checkboxes).filter(cb => cb.checked);
                
                if (checkedBoxes.length > 2) {
                    this.checked = false;
                    alert("You can only select up to two options.");
                }
            });
        });
    }

    function validateTextInput(inputSelector) {
        const inputField = document.querySelector(inputSelector);

        inputField.addEventListener("blur", function () { // Validate when user leaves the field
            let value = this.value.trim();

            if (value === "") return; // Allow empty input

            let valuesArray = value.split(",").map(item => item.trim());
            let commaCount = (value.match(/,/g) || []).length;

            // Allow only one value OR exactly two values separated by a single comma (No extra spaces)
            if (!(valuesArray.length === 1 || (valuesArray.length === 2 && commaCount === 1)) || valuesArray.some(v => v === "")) {
                alert("Please enter either one value or exactly two values separated by a single comma (no extra spaces).");
                this.value = "";  // Clear invalid input
            }
        });

        inputField.addEventListener("input", function () {
            let value = this.value;
            let commaCount = (value.match(/,/g) || []).length;

            // Prevent more than one comma
            if (commaCount > 1) {
                alert("You can only use one comma.");
                this.value = value.slice(0, value.lastIndexOf(",")); // Remove extra comma
            }

            // Prevent typing after valid input
            let valuesArray = value.split(",").map(item => item.trim());
            if (valuesArray.length > 2) {
                alert("Only one or two values allowed. No extra spaces.");
                this.value = valuesArray.slice(0, 2).join(", "); // Keep only first two valid values
            }
        });
    }

    // Apply validation to checkboxes
    validateCheckboxes("courses");
    validateCheckboxes("interests");
    validateCheckboxes("time_period");

    // Enforce one or two-course input in text fields
    validateTextInput('input[name="custom_course"]');
    validateTextInput('input[name="custom_interest"]');
});
