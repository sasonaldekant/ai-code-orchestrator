namespace InsuranceSystem.Backend.Models
{
    public class Policy
    {
        public int Id { get; set; }
        public string PolicyNumber { get; set; }
        public decimal PremiumAmount { get; set; }
        public DateTime StartDate { get; set; }
        public DateTime EndDate { get; set; }
        public int CustomerId { get; set; }
        
        // Navigation property
        public virtual Customer Customer { get; set; }
    }
}
