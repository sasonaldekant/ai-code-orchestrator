using Microsoft.EntityFrameworkCore;
using InsuranceSystem.Backend.Models;

namespace InsuranceSystem.Backend
{
    public class InsuranceContext : DbContext
    {
        public InsuranceContext(DbContextOptions<InsuranceContext> options) : base(options) { }

        public DbSet<Policy> Policies { get; set; }
        public DbSet<Customer> Customers { get; set; }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<Policy>()
                .HasOne(p => p.Customer)
                .WithMany(c => c.Policies)
                .HasForeignKey(p => p.CustomerId);
        }
    }
}
