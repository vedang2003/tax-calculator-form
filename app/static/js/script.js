// Tax Calculator Form Handler
class TaxCalculatorForm {
  constructor() {
    this.form = document.getElementById("taxForm");
    this.submitBtn = this.form.querySelector(".submit-btn");
    this.loading = this.form.querySelector(".loading");
    this.successMsg = this.form.querySelector(".success-message");
    this.errorMsg = this.form.querySelector(".error-message");
    this.isSubmitting = false;
    this.hasValidationErrors = false;
    this.init();
  }

  init() {
    this.bindEvents();
    this.setupValidation();
    this.setupDistrictDropdown();
  }

  setupDistrictDropdown() {
    const stateSelect = document.getElementById("state");
    const districtSelect = document.getElementById("district");

    if (!stateSelect || !districtSelect) return;

    stateSelect.addEventListener("change", () => {
      const selectedState = stateSelect.value;
      const districts = DISTRICT_DATA[selectedState] || [];

      // Clear previous options
      districtSelect.innerHTML = '<option value="">Select District</option>';

      // Populate new options
      districts.forEach((district) => {
        const option = document.createElement("option");
        option.value = district.toLowerCase().replace(/\s+/g, "-");
        option.textContent = district;
        districtSelect.appendChild(option);
      });

      // Reset district selection
      districtSelect.value = "";
    });
  }

  bindEvents() {
    this.form.addEventListener("submit", (e) => this.handleSubmit(e));

    // Add real-time validation
    const inputs = this.form.querySelectorAll(
      "input[required], select[required]"
    );
    inputs.forEach((input) => {
      input.addEventListener("blur", () => this.validateField(input));
      input.addEventListener("input", () => this.clearFieldError(input));
    });
  }

  setupValidation() {
    // Add visual indicators for required fields
    const requiredInputs = this.form.querySelectorAll(
      "input[required],select[required]"
    );
    requiredInputs.forEach((input) => {
      const label = this.form.querySelector(`label[for="${input.id}"]`);
      if (label && !label.textContent.includes("*")) {
        label.innerHTML += ' <span style="color: #e74c3c;">*</span>';
      }
    });
  }

  async handleSubmit(e) {
    e.preventDefault();

    if (this.isSubmitting) return;
    this.isSubmitting = true;

    if (!this.validateForm()) {
      this.isSubmitting = false;
      return;
    }
    const formData = new FormData(this.form);
    this.showLoading();
    try {
      const response = await this.submitForm(formData);

      const result = await response.json();
      if (response.ok && result.message === "Success") {
        this.showSuccess();
        this.resetForm();
      } else {
        const serverErrorMessage = result.error || `Server error: ${response.status}`;
        console.error("Server error:", serverErrorMessage);
        this.showError(serverErrorMessage);
      }
    } catch (error) {
      console.error("Form submission error:", error);
      this.showError();
    } finally {
      this.isSubmitting = false;
      this.hideLoading();
    }
  }

  async submitForm(formData) {
    const csrfToken = this.form.querySelector('input[name="csrf_token"]').value;
    try {
      const response = await fetch("/submit", {
        method: "POST",
        headers: {
          "X-CSRF-Token": csrfToken
        },
        body: formData,
      });

      console.log("Response status:", response.status);
      console.log("Response headers:", response.headers);

      return response;
    } catch (error) {
      console.error("Network error:", error);
      throw error;
    }
  }

  validateForm() {
    const requiredFields = this.form.querySelectorAll(
      "input[required], select[required]"
    );
    let isValid = true;

    requiredFields.forEach((field) => {
      if (!this.validateField(field)) {
        isValid = false;
      }
    });

    if (!isValid) {
      const firstError = this.form.querySelector(".field-error");
      if (firstError) {
        firstError.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }
    return isValid;
  }

  validateField(field) {
    if (field.hasAttribute("required") && !field.value.trim()) {
      this.showFieldError(field, "This field is required");
      return false;
    }

    // Validate email format
    if (field.type === "email" && field.value.trim()) {
      if (!this.isValidEmail(field.value)) {
        this.showFieldError(field, "Please enter a valid email address");
        return false;
      }
    }

    // Validate phone number format
    if (field.type === "tel" && field.value.trim()) {
      if (!this.isValidPhone(field.value)) {
        this.showFieldError(field, "Please enter a valid phone number");
        return false;
      }
    }

    this.clearFieldError(field);
    return true;
  }

  isValidEmail(email) {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  }

  isValidPhone(phone) {
    const phoneRegex = /^(\+91-|\+91|0)?\d{10}$/;
    return phoneRegex.test(phone);
  }

  showFieldError(field, message) {
    this.clearFieldError(field);
    field.classList.add("error");

    const errorDiv = document.createElement("div");
    errorDiv.className = "field-error";
    errorDiv.textContent = message;

    field.parentNode.appendChild(errorDiv);
  }

  clearFieldError(field) {
    field.classList.remove("error");

    const existingError = field.parentNode.querySelector(".field-error");
    if (existingError) {
      existingError.remove();
    }
  }

  showLoading() {
    this.hideMessages();
    this.submitBtn.style.display = "none";
    this.loading.style.display = "block";
    this.form.style.pointerEvents = "none";
    // Disable all form elements
    const formElements = this.form.querySelectorAll("input, select, button");
    formElements.forEach((element) => (element.disabled = true));
  }

  hideLoading() {
    this.loading.style.display = "none";
    this.submitBtn.style.display = "block";
    this.form.style.pointerEvents = "auto";

    // Re-enable all form elements
    const formElements = this.form.querySelectorAll("input, select, button");
    formElements.forEach((element) => (element.disabled = false));
  }

  showSuccess() {
    this.hideMessages();
    this.successMsg.style.display = "block";
    this.successMsg.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  showError(message = "An error occurred. Please try again later.") {
    this.hideMessages();
    this.errorMsg.textContent = message;
    this.errorMsg.style.display = "block";
    this.errorMsg.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  hideMessages() {
    this.successMsg.style.display = "none";
    this.errorMsg.style.display = "none";
  }

  resetForm() {
    this.form.reset();

    // Clear any field errors
    const fieldErrors = this.form.querySelectorAll(".field-error");
    fieldErrors.forEach((error) => error.remove());

    // Reset field styles
    const fields = this.form.querySelectorAll("input, select");
    fields.forEach((field) => {
      field.classList.remove("error");
    });

    this.hasValidationErrors = false;
  }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  new TaxCalculatorForm();

  // Add smooth scroll behavior
  document.documentElement.style.scrollBehavior = "smooth";

  // Add loading animation delay for better UX
  setTimeout(() => {
    document.body.style.opacity = "1";
  }, 100);
});

// District data configuration
const DISTRICT_DATA = {
  "uttar-pradesh": [
    "Agra",
    "Aligarh",
    "Amroha",
    "Auraiya",
    "Ayodhya",
    "Azamgarh",
    "Baghpat",
    "Bahraich",
    "Ballia",
    "Balrampur",
    "Banda",
    "Barabanki",
    "Bareilly",
    "Basti",
    "Bhadohi",
    "Bijnor",
    "Budaun",
    "Bulandshahr",
    "Chandauli",
    "Chitrakoot",
    "Deoria",
    "Etah",
    "Etawah",
    "Farrukhabad",
    "Fatehpur",
    "Firozabad",
    "Gautam Buddha Nagar",
    "Ghaziabad",
    "Ghazipur",
    "Gonda",
    "Gorakhpur",
    "Hamirpur",
    "Hapur",
    "Hardoi",
    "Hathras",
    "Jalaun",
    "Jaunpur",
    "Jhansi",
    "Kannauj",
    "Kanpur Dehat",
    "Kanpur Nagar",
    "Kasganj",
    "Kaushambi",
    "Kushinagar",
    "Lakhimpur Kheri",
    "Lalitpur",
    "Lucknow",
    "Maharajganj",
    "Mahoba",
    "Mainpuri",
    "Mathura",
    "Mau",
    "Meerut",
    "Mirzapur",
    "Moradabad",
    "Muzaffarnagar",
    "Pilibhit",
    "Pratapgarh",
    "Prayagraj",
    "Raebareli",
    "Rampur",
    "Saharanpur",
    "Sambhal",
    "Sant Kabir Nagar",
    "Shahjahanpur",
    "Shamli",
    "Shravasti",
    "Siddharthnagar",
    "Sitapur",
    "Sonbhadra",
    "Sultanpur",
    "Unnao",
    "Varanasi",
  ],
  uttarakhand: [
    "Almora",
    "Bageshwar",
    "Chamoli",
    "Champawat",
    "Dehradun",
    "Haridwar",
    "Nainital",
    "Pauri Garhwal",
    "Pithoragarh",
    "Rudraprayag",
    "Tehri Garhwal",
    "Udham Singh Nagar",
    "Uttarkashi",
  ],
};
