<template>
  <div id="app">
    <div class="container">
      <div class="page-header">
        <h1>SitRaman</h1>
      </div>

      <!-- Flash Message -->
      <div class="table-responsive">
        <table class="table">
          <tr>
            <td>Status:</td>
            <td><span id="flash_message"></span></td>
          </tr>
        </table>
      </div>

      <div class="col-md-12" id="form_data">
        Create, Update, Classification and Delete :
        <div class="well">
          <div class="form-horizontal">
            <div class="form-group">
              <label class="control-label col-sm-2" for="wishlist_id"
                >请输入物质名称的CAS号：</label
              >
              <div class="col-sm-6">
                <input
                  type="text"
                  class="form-control"
                  id="wishlist_id"
                  placeholder="Enter ID of CAS"
                />
                <button type="submit" class="btn btn-primary" id="query-btn">
                  query
                </button>
              </div>

              <input type="file" class="btn btn-primary" id="file-loader" multiple />
              <div class="col-sm-4">
                <button type="submit" class="btn btn-primary" id="retrieve-btn">
                  create
                </button>
                <button type="submit" class="btn btn-danger" id="update-btn">
                  update
                </button>
                <button type="button" class="btn btn-light" id="delete-btn">
                  delete
                </button>
                <button type="button" class="btn btn-primary" id="item-classify-btn">
                  classification
                </button>
              </div>
              <div class="graph">
                <h4>graph</h4>
                <div id="echarts" style="height: 300px; width: 300px;"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      spectrums: [],
    };
  },
  methods: {},
};
</script>

<style></style>
