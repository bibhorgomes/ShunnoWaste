function openOrderForm() {
    document.getElementById("orderFormModal").style.display = "flex";
  }
  
  function closeOrderForm() {
    document.getElementById("orderFormModal").style.display = "none";
  }
  
  function submitOrder() {
    
    const form = document.getElementById("orderForm");
    
    
    form.reset();
  
    
    document.getElementById("orderFormModal").style.display = "none";
    
    
    document.getElementById("successMessage").style.display = "flex";
  }
  
  function closeSuccessMessage() {
    document.getElementById("successMessage").style.display = "none";
  }
  