document.addEventListener("DOMContentLoaded", function (){
    function getValue(id){
        let el=document.getElementById(id);
        return el ? parseFloat(el.value) || 0 : 0;

    }
    function calculateSalary()
    {
        let basic=getValue("id_basic_salary");
        let house=getValue("id_house_allowance");
        let da=getValue("id_da_allowance");
        let other=getValue("id_other_allowance");
        let ot=getValue("id_ot_amount");

        let pf=getValue("id_pf");
        let advance=getValue("id_advance");
        let loan=getValue("id_loan");

        let working=getValue("id_working_days");
        let absent=getValue("id_absent_days");

        let gross=Math.round(basic+house+da+other+ot);
        
        let lopBase=basic+house+da+other;
        let lop=working>0 ? Math.round((lopBase /working )* absent) :0 ;
        
       

        let deduction=Math.round(pf+advance+loan+lop);

        let net=Math.round(gross-deduction);

        

        if (document.getElementById("id_gross_salary"))
            document.getElementById("id_gross_salary").value=gross.toFixed(2);

        if (document.getElementById("id_absent_amount")) {
            document.getElementById("id_absent_amount").value = "₹ " + lop.toFixed(2);
        
        }

        if(document.getElementById("id_total_deduction"))
            document.getElementById("id_total_deduction").value=deduction.toFixed(2);

       
        if(document.getElementById("id_net_salary"))
            document.getElementById("id_net_salary").value=net.toFixed(2);

    }
    document.querySelectorAll("input,select").forEach(function (el){
        el.addEventListener("input",calculateSalary);
        el.addEventListener("change",calculateSalary);
    });
    calculateSalary()
    
})
