using System.Collections.Generic;
using System.Threading.Tasks;
using API.DTOs;
using API.DbContext;

namespace API.Managers
{
  public class EquipmentManager
  {
    private readonly DefaultDbContext _dbContext;

    public EquipmentManager(DefaultDbContext dbContext)
    {
      _dbContext = dbContext;
    }

    public async Task<List<AssetDTO>> GetAssetInfo()
    {
      var assetList = await _dbContext.GetAssetsAsync();
      return assetList;
    }
  }
}
