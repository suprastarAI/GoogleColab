/**
 * Gmail → Google Drive: Simpan PDF tagihan kartu kredit ke folder Drive.
 *
 * Setup:
 * 1. Buka script.google.com → New Project
 * 2. Paste kode ini → Save
 * 3. Run sekali manual untuk authorize (Gmail + Drive permissions)
 * 4. Tambahkan Time-based trigger: monthly, hari ke-1 pukul 06:00–07:00 WIB
 *
 * Folder struktur di Drive:
 *   Tagihan_KK/
 *     2026-06/
 *       BCA_tagihan_202606.pdf
 *       DBS_tagihan_202606.pdf
 *       ...
 */

var DRIVE_ROOT_FOLDER = "Tagihan_KK";   // folder utama di My Drive

// Kata kunci pencarian di Gmail — sesuaikan dengan subject email dari bank
var BANK_SEARCH_RULES = [
  {
    query: 'from:(@bca.co.id) subject:(e-Statement OR eBilling OR tagihan) has:attachment filename:pdf',
    prefix: 'BCA_'
  },
  {
    query: 'from:(dbs.com OR dbsdigibank.id) subject:(e-Statement OR statement) has:attachment filename:pdf',
    prefix: 'DBS_'
  },
  {
    query: 'from:(@bankmandiri.co.id) subject:(e-Statement OR tagihan) has:attachment filename:pdf',
    prefix: 'Mandiri_'
  },
  {
    query: 'from:(@cimb.co.id OR @cimbniaga.co.id) subject:(e-Statement OR tagihan) has:attachment filename:pdf',
    prefix: 'CIMB_'
  },
  {
    query: 'from:(@bni.co.id) subject:(e-Statement OR tagihan) has:attachment filename:pdf',
    prefix: 'BNI_'
  },
  {
    query: 'from:(@bankbsi.co.id OR @bsm.co.id) subject:(e-Statement OR tagihan) has:attachment filename:pdf',
    prefix: 'BSI_'
  },
  {
    query: 'from:(@bankmega.co.id OR @megacard.co.id) subject:(e-Statement OR tagihan) has:attachment filename:pdf',
    prefix: 'Mega_'
  },
];

// Label Gmail yang ditambahkan setelah diproses (agar tidak diproses ulang)
var PROCESSED_LABEL = "KK_Processed";

/**
 * Entry point — jalankan dari trigger atau secara manual.
 */
function saveTagihanToDrive() {
  var today = new Date();
  // Ambil tagihan bulan LALU (email biasanya masuk di akhir bulan)
  var targetDate = new Date(today.getFullYear(), today.getMonth() - 1, 1);
  var yearMonth = Utilities.formatDate(targetDate, "Asia/Jakarta", "yyyy-MM");

  var rootFolder = getOrCreateFolder_(null, DRIVE_ROOT_FOLDER);
  var monthFolder = getOrCreateFolder_(rootFolder, yearMonth);
  var label = getOrCreateLabel_(PROCESSED_LABEL);

  var savedCount = 0;

  for (var i = 0; i < BANK_SEARCH_RULES.length; i++) {
    var rule = BANK_SEARCH_RULES[i];
    // Hanya ambil email yang belum berlabel KK_Processed
    var fullQuery = rule.query + ' -label:' + PROCESSED_LABEL
      + ' after:' + formatDateForQuery_(new Date(targetDate.getFullYear(), targetDate.getMonth(), 1))
      + ' before:' + formatDateForQuery_(new Date(today.getFullYear(), today.getMonth(), 1));

    var threads = GmailApp.search(fullQuery, 0, 20);
    for (var t = 0; t < threads.length; t++) {
      var messages = threads[t].getMessages();
      for (var m = 0; m < messages.length; m++) {
        var attachments = messages[m].getAttachments();
        for (var a = 0; a < attachments.length; a++) {
          var att = attachments[a];
          if (att.getContentType() !== 'application/pdf') continue;

          var filename = rule.prefix + yearMonth.replace('-','') + '_' + att.getName();
          // Hindari duplikat
          if (!fileExists_(monthFolder, filename)) {
            monthFolder.createFile(att.copyBlob()).setName(filename);
            savedCount++;
            Logger.log('Saved: ' + filename);
          }
        }
        // Tandai email sudah diproses
        messages[m].getThread().addLabel(label);
      }
    }
  }

  Logger.log('Total PDF tersimpan: ' + savedCount + ' di ' + DRIVE_ROOT_FOLDER + '/' + yearMonth);
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function getOrCreateFolder_(parent, name) {
  var folders = parent
    ? parent.getFoldersByName(name)
    : DriveApp.getFoldersByName(name);
  if (folders.hasNext()) return folders.next();
  return parent ? parent.createFolder(name) : DriveApp.createFolder(name);
}

function getOrCreateLabel_(name) {
  var label = GmailApp.getUserLabelByName(name);
  if (!label) label = GmailApp.createLabel(name);
  return label;
}

function fileExists_(folder, filename) {
  var files = folder.getFilesByName(filename);
  return files.hasNext();
}

function formatDateForQuery_(d) {
  // Format: yyyy/MM/dd (Gmail query format)
  return Utilities.formatDate(d, "UTC", "yyyy/MM/dd");
}
