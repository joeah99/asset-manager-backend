using System;
using API.DTOs;

namespace API.Services
{
    public class AssetDepreciationService 
    {
        public List<AssetDepreciationDTO> StraightLineDepreciation(double initialCost, double salvageValue, int usefulLife)
        {
            List<AssetDepreciationDTO> endOfMonthValues = new List<AssetDepreciationDTO>();
            double annualDepreciation = (initialCost - salvageValue) / usefulLife;
            double monthlyDepreciation = annualDepreciation / 12;
            double bookValue = initialCost;

            DateTime currentDate = new DateTime(DateTime.Now.Year - 1, DateTime.Now.Month, 1);

            for (int month = 1; month <= usefulLife * 12; month++) {
            bookValue -= monthlyDepreciation;
            if (bookValue < salvageValue) {
                bookValue = salvageValue;
            }
            endOfMonthValues.Add(new AssetDepreciationDTO
            {
                DepreciationDate = currentDate.ToString("yyyy-MM-dd"),
                NewBookValue = (float)bookValue
            });
            currentDate = currentDate.AddMonths(1);
            }

            return endOfMonthValues;
        }

        public List<AssetDepreciationDTO> DecliningBalanceDepreciation(double initialCost, double salvageValue, int usefulLife, double rate)
        {
            double bookValue = initialCost;
            List<AssetDepreciationDTO> endOfMonthValues = new List<AssetDepreciationDTO>();

            DateTime currentDate = new DateTime(DateTime.Now.Year - 1, DateTime.Now.Month, 1);

            for (int month = 1; month <= usefulLife * 12; month++) {
            double depreciation = bookValue * rate / 12;
            bookValue -= depreciation;
            if (bookValue < salvageValue) {
                bookValue = salvageValue;
            }
            endOfMonthValues.Add(new AssetDepreciationDTO
            {
                DepreciationDate = currentDate.ToString("yyyy-MM-dd"),
                NewBookValue = (float)bookValue
            });
            currentDate = currentDate.AddMonths(1);
            }

            return endOfMonthValues;
        }

        public List<AssetDepreciationDTO> DoubleDecliningBalanceDepreciation(double initialCost, double salvageValue, int usefulLife)
        {
            return DecliningBalanceDepreciation(initialCost, salvageValue, usefulLife, 2.0 / usefulLife);
        }

        public List<AssetDepreciationDTO> UnitsOfProductionDepreciation(double initialCost, double salvageValue, int totalUnits, int unitsProducedPerYear)
        {
            double depreciationPerUnit = (initialCost - salvageValue) / totalUnits;
            List<AssetDepreciationDTO> endOfMonthValues = new List<AssetDepreciationDTO>();
            double bookValue = initialCost;
            int totalMonths = (int)Math.Ceiling((double)totalUnits / unitsProducedPerYear * 12);

            DateTime currentDate = new DateTime(DateTime.Now.Year - 1, DateTime.Now.Month, 1);

            for (int month = 1; month <= totalMonths; month++)
            {
            int unitsProducedThisMonth = Math.Min(unitsProducedPerYear / 12, totalUnits - (month - 1) * (unitsProducedPerYear / 12));
            bookValue -= depreciationPerUnit * unitsProducedThisMonth;
            if (bookValue < salvageValue)
            {
                bookValue = salvageValue;
            }
            endOfMonthValues.Add(new AssetDepreciationDTO
            {
                DepreciationDate = currentDate.ToString("yyyy-MM-dd"),
                NewBookValue = (float)bookValue
            });
            currentDate = currentDate.AddMonths(1);
            }

            return endOfMonthValues;
        }

        public List<AssetDepreciationDTO> ModifiedAcceleratedCostRecoverySystem(double initialCost, int usefulLife)
        {
            double[] macrsRates = new double[] { 0.20, 0.32, 0.192, 0.1152, 0.1152, 0.0576 };
            List<AssetDepreciationDTO> endOfMonthValues = new List<AssetDepreciationDTO>();
            double bookValue = initialCost;

            DateTime currentDate = new DateTime(DateTime.Now.Year - 1, DateTime.Now.Month, 1);

            for (int year = 0; year < macrsRates.Length; year++)
            {
            double annualDepreciation = initialCost * macrsRates[year];
            double monthlyDepreciation = annualDepreciation / 12;

            for (int month = 1; month <= 12; month++)
            {
                bookValue -= monthlyDepreciation;
                if (bookValue < 0) bookValue = 0; // Ensure book value doesn't go below zero
                endOfMonthValues.Add(new AssetDepreciationDTO
                {
                DepreciationDate = currentDate.ToString("yyyy-MM-dd"),
                NewBookValue = (float)bookValue
                });
                currentDate = currentDate.AddMonths(1);
            }
            }

            return endOfMonthValues;
        }
    }
}